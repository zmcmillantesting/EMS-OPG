from enum import Enum, auto


class WorkflowState(Enum):

    IDLE = auto()

    ORDER_SELECTED = auto() 

    DEVICE_SELECTED = auto()

    TESTING = auto()

    COMPLETE = auto()

    CANCELLED = auto()

    ERROR = auto()