from abc import ABC, abstractmethod
from tkinter import messagebox


class BaseNotifier(ABC):
    @abstractmethod
    def notify_completed(self, job):
        pass


class TkinterNotifier(BaseNotifier):
    def notify_completed(self, job):
        try:
            messagebox.showinfo("Job Completed", f"Completed: {job.description}")
        except Exception:
            pass
