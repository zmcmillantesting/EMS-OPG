from ems_opg.workflow.workflow_engine import WorkflowEngine
from ems_opg.workflow.workflow_state import WorkflowState


def started_engine():
    engine = WorkflowEngine()
    engine.start("4521", "12345.6")
    return engine


def advanced_to_awaiting_result(engine):
    for _ in range(4):
        engine.next_step()
    return engine


def test_start_captures_operator_and_order_and_enters_testing():
    engine = started_engine()

    assert engine.state == WorkflowState.TESTING
    assert engine.session.operator == "4521"
    assert engine.session.order_number == "12345.6"
    assert engine.session.serial_number == ""
    assert engine.session.current_step == 0


def test_next_step_advances_through_all_four_qr_steps_then_awaits_result():
    engine = started_engine()

    for expected_step in (1, 2, 3):
        engine.next_step()
        assert engine.state == WorkflowState.TESTING
        assert engine.session.current_step == expected_step

    engine.next_step()

    assert engine.state == WorkflowState.AWAITING_RESULT
    assert engine.session.current_step == 3


def test_next_step_is_a_noop_outside_testing():
    engine = started_engine()
    engine.state = WorkflowState.AWAITING_RESULT

    engine.next_step()

    assert engine.state == WorkflowState.AWAITING_RESULT
    assert engine.session.current_step == 0


def test_previous_step_walks_back_through_qr_steps():
    engine = started_engine()
    engine.next_step()
    engine.next_step()

    engine.previous_step()

    assert engine.state == WorkflowState.TESTING
    assert engine.session.current_step == 1


def test_previous_step_from_awaiting_result_returns_to_testing():
    engine = advanced_to_awaiting_result(started_engine())
    assert engine.state == WorkflowState.AWAITING_RESULT

    engine.previous_step()

    assert engine.state == WorkflowState.TESTING


def test_previous_step_does_not_corrupt_current_step_outside_testing():
    """
    Regression: previous_step() used to decrement current_step whenever
    it was > 0, regardless of state - calling it during a later phase
    silently corrupted where the QR steps would resume.
    """
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("PASS")
    assert engine.state == WorkflowState.AWAITING_SERIAL
    step_before = engine.session.current_step

    engine.previous_step()

    assert engine.state == WorkflowState.AWAITING_SERIAL
    assert engine.session.current_step == step_before


def test_set_test_result_pass_moves_to_awaiting_serial():
    engine = advanced_to_awaiting_result(started_engine())

    engine.set_test_result("PASS")

    assert engine.state == WorkflowState.AWAITING_SERIAL
    assert engine.session.test_result == "PASS"


def test_set_test_result_fail_skips_serial_and_mac_entirely():
    engine = advanced_to_awaiting_result(started_engine())

    engine.set_test_result("FAIL", notes="fails -LL during functional test")

    assert engine.state == WorkflowState.READY_TO_SAVE
    assert engine.session.test_result == "FAIL"
    assert engine.session.test_notes == "fails -LL during functional test"


def test_set_test_result_is_a_noop_before_qr_steps_are_done():
    engine = started_engine()

    engine.set_test_result("PASS")

    assert engine.state == WorkflowState.TESTING
    assert engine.session.test_result == ""


def test_set_serial_number_advances_to_assigning_mac():
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("PASS")

    engine.set_serial_number("EM20260001")

    assert engine.state == WorkflowState.ASSIGNING_MAC
    assert engine.session.serial_number == "EM20260001"


def test_set_serial_number_is_a_noop_outside_awaiting_serial():
    engine = started_engine()

    engine.set_serial_number("EM20260001")

    assert engine.session.serial_number == ""


def test_set_mac_addresses_stores_values_and_stays_in_assigning_mac():
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("PASS")
    engine.set_serial_number("EM20260001")

    engine.set_mac_addresses("00:11:22:33:44:01", "00:11:22:33:44:02")

    assert engine.state == WorkflowState.ASSIGNING_MAC
    assert engine.session.mac1 == "00:11:22:33:44:01"
    assert engine.session.mac2 == "00:11:22:33:44:02"


def test_set_mac_addresses_is_a_noop_outside_assigning_mac():
    engine = started_engine()

    engine.set_mac_addresses("00:11:22:33:44:01", "00:11:22:33:44:02")

    assert engine.session.mac1 == ""


def test_confirm_mac_assignment_requires_both_macs_already_set():
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("PASS")
    engine.set_serial_number("EM20260001")

    engine.confirm_mac_assignment()

    assert engine.state == WorkflowState.ASSIGNING_MAC


def test_confirm_mac_assignment_advances_to_verifying_mac():
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("PASS")
    engine.set_serial_number("EM20260001")
    engine.set_mac_addresses("00:11:22:33:44:01", "00:11:22:33:44:02")

    engine.confirm_mac_assignment()

    assert engine.state == WorkflowState.VERIFYING_MAC


def test_confirm_mac_verification_advances_to_ready_to_save():
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("PASS")
    engine.set_serial_number("EM20260001")
    engine.set_mac_addresses("00:11:22:33:44:01", "00:11:22:33:44:02")
    engine.confirm_mac_assignment()

    engine.confirm_mac_verification()

    assert engine.state == WorkflowState.READY_TO_SAVE


def test_confirm_mac_verification_is_a_noop_outside_verifying_mac():
    engine = started_engine()

    engine.confirm_mac_verification()

    assert engine.state == WorkflowState.TESTING


def test_restart_keeps_operator_and_order_and_clears_everything_else():
    engine = advanced_to_awaiting_result(started_engine())
    engine.set_test_result("FAIL", notes="bad LED")

    engine.restart()

    assert engine.state == WorkflowState.TESTING
    assert engine.session.operator == "4521"
    assert engine.session.order_number == "12345.6"
    assert engine.session.serial_number == ""
    assert engine.session.test_result == ""
    assert engine.session.current_step == 0


def test_cancel_marks_session_cancelled():
    engine = started_engine()

    engine.cancel()

    assert engine.state == WorkflowState.CANCELLED
    assert engine.session.cancelled is True


def test_current_step_name_matches_step_names_table():
    engine = started_engine()

    assert engine.current_step_name() == "Username"
    engine.next_step()
    assert engine.current_step_name() == "Password"