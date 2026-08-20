from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkflowSession:

    operator: str = ""

    order_number: str = ""

    # Only ever set on the PASS branch, during AWAITING_SERIAL - a failed
    # board never gets one.
    serial_number: str = ""

    mac1: str = ""

    mac2: str = ""

    test_result: str = ""

    test_notes: str = ""

    current_step: int = 0

    # The four functional-test QR steps only - MAC/serial capture are
    # tracked as WorkflowState values instead (see workflow_engine.py).
    total_steps: int = 4

    started: datetime = field(default_factory=datetime.now)

    finished: datetime | None = None

    cancelled: bool = False

    completed: bool = False