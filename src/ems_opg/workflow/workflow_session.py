from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkflowSession:

    operator: str = ""

    order_number: str = ""

    # Captured at session/start now, before the functional test runs -
    # not at the end like the old serial-number screen.
    serial_number: str = ""

    mac1: str = ""

    mac2: str = ""

    test_result: str = ""

    test_notes: str = ""

    current_step: int = 0

    # Only the four functional-test QR steps live on this counter - MAC
    # assignment/verification are tracked as WorkflowState values instead
    # (see workflow_engine.py), not additional step indexes.
    total_steps: int = 4

    started: datetime = field(default_factory=datetime.now)

    finished: datetime | None = None

    cancelled: bool = False

    completed: bool = False