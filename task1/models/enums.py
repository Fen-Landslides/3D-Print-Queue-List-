from enum import Enum


class JobStatus(Enum):
    WAITING = "waiting"
    SERVING = "serving"
    DONE = "done"
