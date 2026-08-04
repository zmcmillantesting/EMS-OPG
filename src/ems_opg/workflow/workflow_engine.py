from datetime import datetime

from ems_opg.workflow.workflow_session import WorkflowSession
from ems_opg.workflow.workflow_state import WorkflowState


class WorkflowEngine:

    STEP_NAMES = [

        "Check Drives",

        "Loopback Ports 2-4",

        "Loopback Ports 5-8",

        "Initialize Ethernet",

        "System Information",

        "Program MAC Address 1",

        "Program MAC Address 2",

        "Verify MAC Addresses",

    ]

    def __init__(self):

        self.state = WorkflowState.IDLE

        self.session = WorkflowSession()

    # --------------------------------------------------

    def start(
        self,
        operator,
        order_number,
        serial_number,
        mac1,
        mac2,
    ):

        self.session = WorkflowSession(

            operator=operator,

            order_number=order_number,

            serial_number=serial_number,

            mac1=mac1,

            mac2=mac2,

            current_step=0,

        )

        self.state = WorkflowState.TESTING

    # --------------------------------------------------

    def next_step(self):

        if self.state != WorkflowState.TESTING:
            return

        if self.session.current_step < self.session.total_steps - 1:

            self.session.current_step += 1

        else:

            self.complete()

    # --------------------------------------------------

    def previous_step(self):

        if self.session.current_step > 0:

            self.session.current_step -= 1

    # --------------------------------------------------

    def current_step_name(self):

        return self.STEP_NAMES[
            self.session.current_step
        ]

    # --------------------------------------------------

    def complete(self):

        self.session.completed = True

        self.session.finished = datetime.now()

        self.state = WorkflowState.COMPLETE

    # --------------------------------------------------

    def cancel(self):

        self.session.cancelled = True

        self.session.finished = datetime.now()

        self.state = WorkflowState.CANCELLED

    # --------------------------------------------------

    def reset(self):

        self.session = WorkflowSession()

        self.state = WorkflowState.IDLE