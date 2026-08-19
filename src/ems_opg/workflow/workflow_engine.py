from datetime import datetime

from ems_opg.workflow.workflow_session import WorkflowSession
from ems_opg.workflow.workflow_state import WorkflowState


class WorkflowEngine:

    # Only the four functional-test QR steps are driven by current_step.
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

    def start(self, operator, order_number, serial_number):
        """Serial number is captured here now, before testing runs."""

        self.session = WorkflowSession(
            operator=operator,
            order_number=order_number,
            serial_number=serial_number,
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
            # Last QR step confirmed - straight to the Pass/Fail prompt.
            self.state = WorkflowState.AWAITING_RESULT

    # --------------------------------------------------

    def previous_step(self):
        if self.state == WorkflowState.AWAITING_RESULT:
            self.state = WorkflowState.TESTING
        elif self.session.current_step > 0:
            self.session.current_step -= 1

    # --------------------------------------------------

    def current_step_name(self):
        return self.STEP_NAMES[self.session.current_step]

    # --------------------------------------------------

    def set_test_result(self, result, notes=""):
        """
        FAIL has no MAC step at all and goes straight to READY_TO_SAVE.
        PASS moves into the MAC sub-flow and only becomes save-ready once
        that's verified.
        """

        if self.state != WorkflowState.AWAITING_RESULT:
            return

        self.session.test_result = result
        self.session.test_notes = notes

        self.state = (
            WorkflowState.ASSIGNING_MAC if result == "PASS"
            else WorkflowState.READY_TO_SAVE
        )

    # --------------------------------------------------

    def set_mac_addresses(self, mac1, mac2):
        """
        PASS branch only. The route handler validates mac1/mac2 against
        the MAC pool before calling this (this class has no DB access) -
        by the time it's called both addresses are already known good.
        Stays in ASSIGNING_MAC; confirm_mac_assignment() advances further.
        """

        if self.state != WorkflowState.ASSIGNING_MAC:
            return

        self.session.mac1 = mac1
        self.session.mac2 = mac2

    # --------------------------------------------------

    def confirm_mac_assignment(self):
        """Operator has reviewed the assigned pair and is ready to verify."""

        if self.state != WorkflowState.ASSIGNING_MAC:
            return

        if not (self.session.mac1 and self.session.mac2):
            return

        self.state = WorkflowState.VERIFYING_MAC

    # --------------------------------------------------

    def confirm_mac_verification(self):
        """Operator confirmed the scanned-back values match. Save-ready."""

        if self.state != WorkflowState.VERIFYING_MAC:
            return

        self.state = WorkflowState.READY_TO_SAVE

    # --------------------------------------------------

    def restart(self):
        """
        Return to the serial/order prompt for the next device, keeping
        the same operator logged in. Used after every save - whether the
        previous device passed or failed - per the "restart the test
        procedure" workflow decision. There is no separate per-device
        "next unit" path anymore; this is the only way back to TESTING.
        """

        operator = self.session.operator
        self.session = WorkflowSession(operator=operator)
        self.state = WorkflowState.IDLE

    # --------------------------------------------------

    def cancel(self):
        self.session.cancelled = True
        self.session.finished = datetime.now()
        self.state = WorkflowState.CANCELLED

    # --------------------------------------------------

    def reset(self):
        self.session = WorkflowSession()
        self.state = WorkflowState.IDLE