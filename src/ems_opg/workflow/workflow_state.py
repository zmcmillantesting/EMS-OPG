from enum import Enum, auto


class WorkflowState(Enum):

    IDLE = auto()

    # Operator has entered order + serial number; running the four
    # functional-test QR steps.
    TESTING = auto()

    # QR steps are done; waiting on the Pass/Fail decision.
    AWAITING_RESULT = auto()

    # PASS branch only: operator scans MAC1, app auto-assigns MAC2.
    ASSIGNING_MAC = auto()

    # PASS branch only: operator confirms the scanned-back values match.
    VERIFYING_MAC = auto()

    # FAIL lands here right after notes are recorded; PASS lands here
    # after MAC verification is confirmed. Either way the session just
    # needs to be persisted.
    READY_TO_SAVE = auto()

    CANCELLED = auto()

    ERROR = auto()