from datetime import datetime

from ems_opg.workflow.workflow_session import WorkflowSession
from ems_opg.workflow.workflow_state import WorkflowState


class WorkflowEngine:

    STEP_NAMES = [

        "Username",

        "Password",

        "Functional Test",

        "System Information",

        "Mac Addresses",

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
    ):

        self.session = WorkflowSession(

            operator=operator,

            order_number=order_number,

            current_step=0,

        )

        self.state = WorkflowState.TESTING

    # --------------------------------------------------

    def set_mac_addresses(self, mac1, mac2):
        if self.state != WorkflowState.TESTING:
            return

        self.session.mac1 = mac1
        self.session.mac2 = mac2

    # --------------------------------------------------

    def set_test_result(self, result, notes=""):
        if self.state != WorkflowState.COMPLETE:
            return

        self.session.test_result = result
        self.session.test_notes = notes

    # --------------------------------------------------

    def finish(self, serial_number):
        self.session.serial_number = serial_number

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

        if self.state == WorkflowState.COMPLETE:
            self.session.completed = False
            self.state = WorkflowState.TESTING

        elif self.session.current_step > 0:

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