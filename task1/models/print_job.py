from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from models.enums import JobStatus


@dataclass
class PrintJob:
    job_id: str
    description: str
    eta_min: Optional[int] = None
    material: Optional[str] = None
    status: JobStatus = JobStatus.WAITING
    order: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def start(self):
        if self.status != JobStatus.WAITING:
            raise ValueError("Only waiting jobs can be started.")
        self.status = JobStatus.SERVING
        self.started_at = datetime.utcnow()
        self.finished_at = None

    def complete(self):
        if self.status != JobStatus.SERVING:
            raise ValueError("Only serving jobs can be completed.")
        self.status = JobStatus.DONE
        self.finished_at = datetime.utcnow()

    def return_to_waiting(self):
        self.status = JobStatus.WAITING
        self.finished_at = None

    def used_minutes(self):
        if self.started_at and self.finished_at:
            return int((self.finished_at - self.started_at).total_seconds() // 60)
        return None
