from ems_opg.workflow.workflow_state import WorkflowState


class WorkflowEngine:

    def __init__(self):

        self.state = WorkflowState.IDLE

    def select_order(self, order):

        self.order = order

        self.state = WorkflowState.ORDER_SELECTED

    def select_device(self, device):

        self.device = device

        self.state = WorkflowState.DEVICE_SELECTED

    def start_test(self):

        self.state = WorkflowState.TESTING

    def complete(self):

        self.state = WorkflowState.COMPLETE

    def reset(self):

        self.order = None

        self.device = None

        self.state = WorkflowState.IDLE