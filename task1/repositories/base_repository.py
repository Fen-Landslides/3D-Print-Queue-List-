from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def get_all_jobs(self):
        pass

    @abstractmethod
    def get_job(self, job_id: str):
        pass

    @abstractmethod
    def save_job(self, job):
        pass

    @abstractmethod
    def delete_job(self, job_id: str):
        pass

    @abstractmethod
    def load_config(self):
        pass

    @abstractmethod
    def save_config(self, config):
        pass
