from enum import Enum, auto


class WorkflowState(Enum):

    IDLE = auto()

    # Operator + order are already selected (home screen); running the
    # four functional-test QR steps for the current board.
    TESTING = auto()

    # QR steps done; waiting on the Pass/Fail decision.
    AWAITING_RESULT = auto()

    # PASS branch only: board is known-good, waiting for the operator to
    # scan/enter its serial number before anything else happens.
    AWAITING_SERIAL = auto()

    # PASS branch only, after serial is captured: operator scans MAC1,
    # app auto-assigns MAC2.
    ASSIGNING_MAC = auto()

    # PASS branch only: operator confirms the scanned-back values match.
    VERIFYING_MAC = auto()

    # FAIL lands here right after a reason is recorded; PASS lands here
    # after MAC verification is confirmed. Either way the attempt just
    # needs to be persisted (a Device row for PASS, an OrderFailure row
    # for FAIL).
    READY_TO_SAVE = auto()

    CANCELLED = auto()

    ERROR = auto()