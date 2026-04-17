import csv


class ExportService:
    def __init__(self, repository):
        self.repository = repository

    def export_all_jobs_csv(self, path: str):
        jobs = self.repository.get_all_jobs()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "job_id", "description", "eta_min", "material", "status",
                "created_at", "started_at", "finished_at", "order"
            ])
            for j in jobs:
                writer.writerow([
                    j.job_id, j.description, j.eta_min, j.material, j.status.value,
                    j.created_at, j.started_at, j.finished_at, j.order
                ])

    def export_done_jobs_by_date(self, start_dt, end_dt, path: str):
        jobs = self.repository.get_all_jobs()
        filtered = [
            j for j in jobs
            if j.status.value == "done" and j.finished_at and start_dt <= j.finished_at <= end_dt
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["job_id", "description", "eta_min", "material", "finished_at", "used_minutes"])
            for j in filtered:
                writer.writerow([
                    j.job_id, j.description, j.eta_min, j.material, j.finished_at, j.used_minutes()
                ])
