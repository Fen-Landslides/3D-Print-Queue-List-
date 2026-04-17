import json
import os
from datetime import datetime
from repositories.base_repository import BaseRepository
from models.print_job import PrintJob
from models.queue_config import QueueConfig
from models.enums import JobStatus


class LocalRepository(BaseRepository):
    def __init__(self, file_path="local_data.json"):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            self._write({"config": {"queue_id": "default", "admin_pin": None}, "jobs": []})

    def _read(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _job_to_dict(self, job):
        return {
            "job_id": job.job_id,
            "description": job.description,
            "eta_min": job.eta_min,
            "material": job.material,
            "status": job.status.value,
            "order": job.order,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        }

    def _dict_to_job(self, d):
        return PrintJob(
            job_id=d["job_id"],
            description=d["description"],
            eta_min=d.get("eta_min"),
            material=d.get("material"),
            status=JobStatus(d.get("status", "waiting")),
            order=d.get("order", 0),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.utcnow(),
            started_at=datetime.fromisoformat(d["started_at"]) if d.get("started_at") else None,
            finished_at=datetime.fromisoformat(d["finished_at"]) if d.get("finished_at") else None,
        )

    def get_all_jobs(self):
        data = self._read()
        return [self._dict_to_job(j) for j in data["jobs"]]

    def get_job(self, job_id: str):
        for job in self.get_all_jobs():
            if job.job_id == job_id:
                return job
        raise ValueError("Job not found.")

    def save_job(self, job):
        data = self._read()
        jobs = data["jobs"]
        for i, existing in enumerate(jobs):
            if existing["job_id"] == job.job_id:
                jobs[i] = self._job_to_dict(job)
                self._write(data)
                return
        jobs.append(self._job_to_dict(job))
        self._write(data)

    def delete_job(self, job_id: str):
        data = self._read()
        data["jobs"] = [j for j in data["jobs"] if j["job_id"] != job_id]
        self._write(data)

    def load_config(self):
        c = self._read()["config"]
        return QueueConfig(queue_id=c.get("queue_id", "default"), admin_pin=c.get("admin_pin"))

    def save_config(self, config):
        data = self._read()
        data["config"] = {"queue_id": config.queue_id, "admin_pin": config.admin_pin}
        self._write(data)
