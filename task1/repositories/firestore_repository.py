import os
from datetime import datetime, timezone
from repositories.base_repository import BaseRepository
from models.print_job import PrintJob
from models.queue_config import QueueConfig
from models.enums import JobStatus
import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreRepository(BaseRepository):
    def __init__(self, queue_id="default"):
        self.queue_id = queue_id
        if not firebase_admin._apps:
            cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.exists(cred_path):
                firebase_admin.initialize_app(credentials.Certificate(cred_path))
            else:
                firebase_admin.initialize_app()
        self.db = firestore.client()
        self.jobs_col = self.db.collection("queue_3d_print").document(self.queue_id).collection("jobs")
        self.config_doc = self.db.collection("queue_3d_config").document(self.queue_id)

    def _to_dt(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return value.replace(tzinfo=timezone.utc).astimezone(tz=None).replace(tzinfo=None)

    def _job_to_dict(self, job):
        return {
            "job_id": job.job_id,
            "description": job.description,
            "eta_min": job.eta_min,
            "material": job.material,
            "status": job.status.value,
            "order": job.order,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
        }

    def _dict_to_job(self, d):
        return PrintJob(
            job_id=d["job_id"],
            description=d["description"],
            eta_min=d.get("eta_min"),
            material=d.get("material"),
            status=JobStatus(d.get("status", "waiting")),
            order=d.get("order", 0),
            created_at=self._to_dt(d.get("created_at")) or datetime.utcnow(),
            started_at=self._to_dt(d.get("started_at")),
            finished_at=self._to_dt(d.get("finished_at")),
        )

    def get_all_jobs(self):
        docs = self.jobs_col.stream()
        return [self._dict_to_job(doc.to_dict()) for doc in docs]

    def get_job(self, job_id: str):
        doc = self.jobs_col.document(job_id).get()
        if not doc.exists:
            raise ValueError("Job not found.")
        return self._dict_to_job(doc.to_dict())

    def save_job(self, job):
        self.jobs_col.document(job.job_id).set(self._job_to_dict(job))

    def delete_job(self, job_id: str):
        self.jobs_col.document(job_id).delete()

    def load_config(self):
        doc = self.config_doc.get()
        if not doc.exists:
            return QueueConfig(queue_id=self.queue_id, admin_pin=None)
        d = doc.to_dict()
        return QueueConfig(queue_id=self.queue_id, admin_pin=d.get("admin_pin"))

    def save_config(self, config):
        self.config_doc.set({"queue_id": config.queue_id, "admin_pin": config.admin_pin})
