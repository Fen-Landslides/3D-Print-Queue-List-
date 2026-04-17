from dataclasses import dataclass
from typing import Optional


@dataclass
class QueueConfig:
    queue_id: str = "default"
    admin_pin: Optional[str] = None
