from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkflowSession:

    operator: str = ""

    order_number: str = ""

    serial_number: str = ""

    mac1: str = ""

    mac2: str = ""

    current_step: int = 0

    total_steps: int = 8

    started: datetime = field(default_factory=datetime.now)

    finished: datetime | None = None

    cancelled: bool = False

    completed: bool = False