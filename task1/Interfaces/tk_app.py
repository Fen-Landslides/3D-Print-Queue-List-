import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
import uuid
from models.print_job import PrintJob


class QueueApp:
    def __init__(self, queue_manager, pin_manager, export_service):
        self.queue_manager = queue_manager
        self.pin_manager = pin_manager
        self.export_service = export_service

        self.root = tk.Tk()
        self.root.title("3D Print Queue System")
        self.root.geometry("1180x700")
        self.root.configure(bg="#0f172a")

        self.description_var = tk.StringVar()
        self.eta_var = tk.StringVar()
        self.material_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.waiting_map = {}
        self.serving_map = {}
        self.done_map = {}

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        top = tk.Frame(self.root, bg="#0f172a")
        top.pack(fill="x", padx=12, pady=12)

        title = tk.Label(top, text="3D Print Queue System", font=("Arial", 20, "bold"), fg="white", bg="#0f172a")
        title.pack(side="left")

        pin_text = "PIN Enabled" if self.pin_manager.has_pin() else "No PIN"
        self.pin_label = tk.Label(top, text=pin_text, fg="#cbd5e1", bg="#0f172a")
        self.pin_label.pack(side="right", padx=8)

        form = tk.LabelFrame(self.root, text="Add Print Job", bg="#111827", fg="white", bd=2)
        form.pack(fill="x", padx=12, pady=6)

        tk.Label(form, text="Description", bg="#111827", fg="white").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        tk.Entry(form, textvariable=self.description_var, width=40).grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form, text="ETA (min)", bg="#111827", fg="white").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        tk.Entry(form, textvariable=self.eta_var, width=12).grid(row=0, column=3, padx=8, pady=8)

        tk.Label(form, text="Material / Color", bg="#111827", fg="white").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        tk.Entry(form, textvariable=self.material_var, width=20).grid(row=0, column=5, padx=8, pady=8)

        tk.Button(form, text="Add Job", command=self.add_job, bg="#0ea5e9", fg="white").grid(row=0, column=6, padx=10, pady=8)
        tk.Button(form, text="Start Next", command=self.start_next, bg="#22c55e", fg="white").grid(row=0, column=7, padx=10, pady=8)
        tk.Button(form, text="Set / Remove PIN", command=self.set_pin, bg="#374151", fg="white").grid(row=0, column=8, padx=10, pady=8)

        actions = tk.Frame(self.root, bg="#0f172a")
        actions.pack(fill="x", padx=12, pady=6)
        tk.Button(actions, text="Complete Selected", command=self.complete_selected, bg="#10b981", fg="white").pack(side="left", padx=4)
        tk.Button(actions, text="Return to Waiting", command=self.return_selected, bg="#f59e0b", fg="white").pack(side="left", padx=4)
        tk.Button(actions, text="Delete Selected", command=self.delete_selected, bg="#ef4444", fg="white").pack(side="left", padx=4)
        tk.Button(actions, text="Move Up", command=self.move_up, bg="#6366f1", fg="white").pack(side="left", padx=4)
        tk.Button(actions, text="Move Down", command=self.move_down, bg="#8b5cf6", fg="white").pack(side="left", padx=4)
        tk.Button(actions, text="Export All CSV", command=self.export_all_csv, bg="#334155", fg="white").pack(side="right", padx=4)
        tk.Button(actions, text="Export Done by Date", command=self._export_done_csv, bg="#475569", fg="white").pack(side="right", padx=4)
        tk.Button(actions, text="Refresh", command=self.refresh_all, bg="#1f2937", fg="white").pack(side="right", padx=4)

        content = tk.Frame(self.root, bg="#0f172a")
        content.pack(fill="both", expand=True, padx=12, pady=8)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.waiting_tree = self._build_tree(content, "Waiting Queue", 0)
        self.serving_tree = self._build_tree(content, "In Progress", 1)
        self.done_tree = self._build_tree(content, "Completed", 2)

        bottom = tk.Frame(self.root, bg="#0f172a")
        bottom.pack(fill="x", padx=12, pady=8)
        self.status_bar = tk.Label(bottom, textvariable=self.status_var, anchor="w", bg="#0f172a", fg="#cbd5e1")
        self.status_bar.pack(fill="x")
        self.status_var.set("Ready")

    def _build_tree(self, parent, title, column):
        frame = tk.LabelFrame(parent, text=title, bg="#111827", fg="white", bd=2)
        frame.grid(row=0, column=column, sticky="nsew", padx=6)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        cols = ("id", "description", "eta", "material", "time", "order")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        headers = {
            "id": "ID",
            "description": "Description",
            "eta": "ETA",
            "material": "Material",
            "time": "Time",
            "order": "Order",
        }
        widths = {"id": 70, "description": 130, "eta": 45, "material": 90, "time": 100, "order": 40}
        for key in cols:
            tree.heading(key, text=headers[key])
            tree.column(key, width=widths[key], anchor="center")
        return tree

    def run(self):
        self.root.mainloop()

    def add_job(self):
        try:
            desc = self.description_var.get().strip()
            eta = self.eta_var.get().strip()
            material = self.material_var.get().strip()
            eta_val = int(eta) if eta else None
            if eta_val is not None and eta_val <= 0:
                raise ValueError("ETA must be greater than 0.")
            job = PrintJob(
                job_id=str(uuid.uuid4())[:8],
                description=desc,
                eta_min=eta_val,
                material=material or None,
            )
            self.queue_manager.add_job(job)
            self.description_var.set("")
            self.eta_var.set("")
            self.material_var.set("")
            self.refresh_all()
            self.status_var.set("Job added successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_next(self):
        try:
            job = self.queue_manager.start_next_job()
            self.refresh_all()
            self.status_var.set(f"Started job: {job.description}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def complete_selected(self):
        job_id = self._selected_id(self.serving_tree, self.serving_map)
        if not job_id:
            return
        try:
            self.queue_manager.complete_job(job_id)
            self.refresh_all()
            self.status_var.set("Job completed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_selected(self):
        job_id = self._selected_id(self.serving_tree, self.serving_map) or self._selected_id(self.done_tree, self.done_map)
        if not job_id:
            return
        try:
            pin = self._ask_pin_if_needed()
            self.queue_manager.move_back_to_waiting(job_id)
            self.refresh_all()
            self.status_var.set("Job moved back to waiting.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        job_id = self._selected_id(self.waiting_tree, self.waiting_map) or self._selected_id(self.serving_tree, self.serving_map) or self._selected_id(self.done_tree, self.done_map)
        if not job_id:
            return
        try:
            pin = self._ask_pin_if_needed()
            self.queue_manager.delete_job(job_id)
            self.refresh_all()
            self.status_var.set("Job deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def move_up(self):
        job_id = self._selected_id(self.waiting_tree, self.waiting_map)
        if not job_id:
            return
        try:
            self.queue_manager.move_waiting_job_up(job_id)
            self.refresh_all()
            self.status_var.set("Waiting job moved up.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def move_down(self):
        job_id = self._selected_id(self.waiting_tree, self.waiting_map)
        if not job_id:
            return
        try:
            self.queue_manager.move_waiting_job_down(job_id)
            self.refresh_all()
            self.status_var.set("Waiting job moved down.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_pin(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set / Remove PIN")
        dialog.configure(bg="#111827")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        old_var = tk.StringVar()
        new_var = tk.StringVar()
        confirm_var = tk.StringVar()

        tk.Label(dialog, text="Set / Remove PIN", font=("Arial", 14, "bold"), bg="#111827", fg="white").grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 8), sticky="w")

        tip = "Leave New PIN and Confirm New PIN blank to remove PIN."
        if self.pin_manager.has_pin():
            tip = "Enter old PIN first. Leave new PIN blank to remove it."
        tk.Label(dialog, text=tip, bg="#111827", fg="#cbd5e1", wraplength=320, justify="left").grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="w")

        tk.Label(dialog, text="Old PIN", bg="#111827", fg="white").grid(row=2, column=0, padx=12, pady=6, sticky="w")
        old_entry = tk.Entry(dialog, textvariable=old_var, show="*", width=24)
        old_entry.grid(row=2, column=1, padx=12, pady=6)

        if not self.pin_manager.has_pin():
            old_entry.configure(state="disabled")

        tk.Label(dialog, text="New PIN", bg="#111827", fg="white").grid(row=3, column=0, padx=12, pady=6, sticky="w")
        tk.Entry(dialog, textvariable=new_var, show="*", width=24).grid(row=3, column=1, padx=12, pady=6)

        tk.Label(dialog, text="Confirm New PIN", bg="#111827", fg="white").grid(row=4, column=0, padx=12, pady=6, sticky="w")
        tk.Entry(dialog, textvariable=confirm_var, show="*", width=24).grid(row=4, column=1, padx=12, pady=6)

        def submit():
            try:
                old_pin = old_var.get().strip()
                new_pin = new_var.get().strip()
                confirm_pin = confirm_var.get().strip()

                if new_pin or confirm_pin:
                    if new_pin != confirm_pin:
                        raise ValueError("PIN confirmation does not match.")
                else:
                    new_pin = None

                self.pin_manager.update_pin(old_pin, new_pin)
                self.pin_label.config(text="PIN Enabled" if self.pin_manager.has_pin() else "No PIN")
                self.status_var.set("PIN updated.")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)

        btn_frame = tk.Frame(dialog, bg="#111827")
        btn_frame.grid(row=5, column=0, columnspan=2, padx=12, pady=12, sticky="e")
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg="#374151", fg="white").pack(side="right", padx=4)
        tk.Button(btn_frame, text="Save", command=submit, bg="#0ea5e9", fg="white").pack(side="right", padx=4)

        dialog.columnconfigure(0, weight=0)
        dialog.columnconfigure(1, weight=1)
        old_entry.focus_set()
        dialog.wait_window()

    def export_all_csv(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not path:
                return
            self.export_service.export_all_jobs_csv(path)
            self.status_var.set(f"Exported all jobs to {path}")
            messagebox.showinfo("Export", "All jobs exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_done_csv(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Done by Date")
        dialog.configure(bg="#111827")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        start_var = tk.StringVar()
        end_var   = tk.StringVar()
        tk.Label(dialog, text="Export Completed Jobs by Date",
                 font=("Arial", 13, "bold"),
                 bg="#111827", fg="white").grid(
            row=0, column=0, columnspan=2, padx=16, pady=(14, 8), sticky=tk.W)
        tk.Label(dialog, text="Start Date (YYYY-MM-DD)",
                 bg="#111827", fg="white").grid(
            row=1, column=0, padx=16, pady=6, sticky=tk.W)
        tk.Entry(dialog, textvariable=start_var, width=20).grid(
            row=1, column=1, padx=16, pady=6)
        tk.Label(dialog, text="End Date (YYYY-MM-DD)",
                 bg="#111827", fg="white").grid(
            row=2, column=0, padx=16, pady=6, sticky=tk.W)
        tk.Entry(dialog, textvariable=end_var, width=20).grid(
            row=2, column=1, padx=16, pady=6)

        def submit():
            start_str = start_var.get().strip()
            end_str   = end_var.get().strip()
            try:
                start_dt = datetime.fromisoformat(start_str + "T00:00:00")
                end_dt   = datetime.fromisoformat(end_str   + "T23:59:59")
            except ValueError:
                messagebox.showerror("Error",
                    "Invalid date format. Use YYYY-MM-DD.", parent=dialog)
                return
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")])
            if not path:
                return
            try:
                self.export_service.export_done_jobs_by_date(start_dt, end_dt, path)
                self.status_var.set(f"Exported completed jobs to {path}")
                messagebox.showinfo("Export", "Completed jobs exported successfully.")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)

        btn_frame = tk.Frame(dialog, bg="#111827")
        btn_frame.grid(row=3, column=0, columnspan=2, padx=16, pady=(8, 14), sticky=tk.E)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                  bg="#374151", fg="white").pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_frame, text="Export", command=submit,
                  bg="#0ea5e9", fg="white").pack(side=tk.RIGHT, padx=4)
        dialog.columnconfigure(1, weight=1)
        dialog.wait_window()

    def refresh_all(self):
        self._clear_tree(self.waiting_tree)
        self._clear_tree(self.serving_tree)
        self._clear_tree(self.done_tree)
        self.waiting_map.clear()
        self.serving_map.clear()
        self.done_map.clear()

        waiting = self.queue_manager.list_waiting_jobs()
        serving = self.queue_manager.list_serving_jobs()
        done = self.queue_manager.list_done_jobs()

        for j in waiting:
            iid = self.waiting_tree.insert("", "end", values=(j.job_id, j.description, j.eta_min or "", j.material or "", self._fmt_dt(j.created_at), j.order))
            self.waiting_map[iid] = j.job_id

        for j in serving:
            iid = self.serving_tree.insert("", "end", values=(j.job_id, j.description, j.eta_min or "", j.material or "", self._fmt_dt(j.started_at), j.order))
            self.serving_map[iid] = j.job_id

        for j in done:
            iid = self.done_tree.insert("", "end", values=(j.job_id, j.description, j.eta_min or "", j.material or "", self._fmt_dt(j.finished_at), j.order))
            self.done_map[iid] = j.job_id

        self.pin_label.config(text="PIN Enabled" if self.pin_manager.has_pin() else "No PIN")

    def _clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _selected_id(self, tree, mapping):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item first.")
            return None
        return mapping.get(selected[0])

    def _ask_pin_if_needed(self):
        if self.pin_manager.has_pin():
            pin = simpledialog.askstring("PIN Required", "Enter admin PIN:", show="*") or ""
            self.pin_manager.require_valid_pin(pin)
            return pin
        return ""

    def _fmt_dt(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M") if dt else ""
