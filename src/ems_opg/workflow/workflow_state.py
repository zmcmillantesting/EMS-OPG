from enum import Enum


class WorkflowState(Enum):

    IDLE = "Idle"

    ORDER_SELECTED = "Order Selected"

    DEVICE_SELECTED = "Device Selected"

    TESTING = "Testing"

    COMPLETE = "Complete"

    ERROR = "Error"