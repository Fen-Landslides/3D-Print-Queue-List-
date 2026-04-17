from models.enums import JobStatus


class QueueManager:
    def __init__(self, repository, notifier=None):
        self.repository = repository
        self.notifier = notifier

    def add_job(self, job):
        if not job.description.strip():
            raise ValueError("Description cannot be empty.")
        waiting = [j for j in self.repository.get_all_jobs() if j.status == JobStatus.WAITING]
        job.order = len(waiting) + 1
        self.repository.save_job(job)

    def list_waiting_jobs(self):
        return sorted(
            [j for j in self.repository.get_all_jobs() if j.status == JobStatus.WAITING],
            key=lambda x: x.order
        )

    def list_serving_jobs(self):
        return [j for j in self.repository.get_all_jobs() if j.status == JobStatus.SERVING]

    def list_done_jobs(self):
        return sorted(
            [j for j in self.repository.get_all_jobs() if j.status == JobStatus.DONE],
            key=lambda x: x.finished_at or x.created_at,
            reverse=True
        )

    def start_next_job(self):
        waiting = self.list_waiting_jobs()
        if not waiting:
            raise ValueError("No waiting job.")
        if self.list_serving_jobs():
            raise ValueError("A job is already in progress.")
        job = waiting[0]
        job.start()
        self.repository.save_job(job)
        self._normalize_waiting_order()
        return job

    def complete_job(self, job_id):
        job = self.repository.get_job(job_id)
        job.complete()
        self.repository.save_job(job)
        if self.notifier:
            self.notifier.notify_completed(job)
        return job

    def move_back_to_waiting(self, job_id):
        job = self.repository.get_job(job_id)
        job.return_to_waiting()
        waiting = self.list_waiting_jobs()
        job.order = len(waiting) + 1
        self.repository.save_job(job)
        return job

    def delete_job(self, job_id):
        self.repository.delete_job(job_id)
        self._normalize_waiting_order()

    def move_waiting_job_up(self, job_id):
        waiting = self.list_waiting_jobs()
        for i in range(1, len(waiting)):
            if waiting[i].job_id == job_id:
                waiting[i].order, waiting[i - 1].order = waiting[i - 1].order, waiting[i].order
                self.repository.save_job(waiting[i])
                self.repository.save_job(waiting[i - 1])
                return

    def move_waiting_job_down(self, job_id):
        waiting = self.list_waiting_jobs()
        for i in range(len(waiting) - 1):
            if waiting[i].job_id == job_id:
                waiting[i].order, waiting[i + 1].order = waiting[i + 1].order, waiting[i].order
                self.repository.save_job(waiting[i])
                self.repository.save_job(waiting[i + 1])
                return

    def _normalize_waiting_order(self):
        waiting = self.list_waiting_jobs()
        for i, job in enumerate(waiting, start=1):
            if job.order != i:
                job.order = i
                self.repository.save_job(job)
