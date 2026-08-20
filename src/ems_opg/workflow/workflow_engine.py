from datetime import datetime

from ems_opg.workflow.workflow_session import WorkflowSession
from ems_opg.workflow.workflow_state import WorkflowState


class WorkflowEngine:

    STEP_NAMES = [
        "Username",
        "Password",
        "Functional Test",
        "System Information",
    ]

    def __init__(self):
        self.state = WorkflowState.IDLE
        self.session = WorkflowSession()

    # --------------------------------------------------

    def start(self, operator, order_number):
        """
        Operator and order are chosen once, up front - serial is captured
        later, only if this board turns out to pass.
        """

        self.session = WorkflowSession(
            operator=operator,
            order_number=order_number,
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
            self.state = WorkflowState.AWAITING_RESULT

    # --------------------------------------------------

    def previous_step(self):
        if self.state == WorkflowState.AWAITING_RESULT:
            self.state = WorkflowState.TESTING
        elif self.state == WorkflowState.TESTING and self.session.current_step > 0:
            self.session.current_step -= 1

    # --------------------------------------------------

    def current_step_name(self):
        return self.STEP_NAMES[self.session.current_step]

    # --------------------------------------------------

    def set_test_result(self, result, notes=""):
        """
        FAIL has no serial/MAC step at all - it goes straight to
        READY_TO_SAVE and gets logged as an OrderFailure, not a Device.
        PASS moves into serial capture first, then the MAC sub-flow.
        """

        if self.state != WorkflowState.AWAITING_RESULT:
            return

        self.session.test_result = result
        self.session.test_notes = notes

        self.state = (
            WorkflowState.AWAITING_SERIAL if result == "PASS"
            else WorkflowState.READY_TO_SAVE
        )

    # --------------------------------------------------

    def set_serial_number(self, serial_number):
        """
        PASS branch only. The route handler validates format and
        uniqueness before calling this - by the time it's called the
        serial is already known good.
        """

        if self.state != WorkflowState.AWAITING_SERIAL:
            return

        self.session.serial_number = serial_number
        self.state = WorkflowState.ASSIGNING_MAC

    # --------------------------------------------------

    def set_mac_addresses(self, mac1, mac2):
        if self.state != WorkflowState.ASSIGNING_MAC:
            return

        self.session.mac1 = mac1
        self.session.mac2 = mac2

    # --------------------------------------------------

    def confirm_mac_assignment(self):
        if self.state != WorkflowState.ASSIGNING_MAC:
            return

        if not (self.session.mac1 and self.session.mac2):
            return

        self.state = WorkflowState.VERIFYING_MAC

    # --------------------------------------------------

    def confirm_mac_verification(self):
        if self.state != WorkflowState.VERIFYING_MAC:
            return

        self.state = WorkflowState.READY_TO_SAVE

    # --------------------------------------------------

    def restart(self):
        """
        Loop back to the next board under the same operator + order -
        both were chosen once on the home screen and stay fixed across
        many boards now that serial is captured per-device instead.
        Whether the previous board passed or failed, this is the only
        way back to TESTING.
        """

        operator = self.session.operator
        order_number = self.session.order_number
        self.session = WorkflowSession(operator=operator, order_number=order_number)
        self.state = WorkflowState.TESTING

    # --------------------------------------------------

    def cancel(self):
        self.session.cancelled = True
        self.session.finished = datetime.now()
        self.state = WorkflowState.CANCELLED

    # --------------------------------------------------

    def reset(self):
        self.session = WorkflowSession()
        self.state = WorkflowState.IDLE