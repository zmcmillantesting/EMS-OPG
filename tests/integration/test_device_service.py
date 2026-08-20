import pytest

from ems_opg.database.models import Device, MACAddressPool, Order
from ems_opg.services.device_service import DeviceService


def seed_order_and_pool(session, order_number="12345.6", quantity=5, mac_count=4):
    session.add(Order(order_number=order_number, quantity=quantity))
    session.add_all([
        MACAddressPool(mac_address=f"AA:BB:CC:DD:EE:{i:02d}")
        for i in range(mac_count)
    ])
    session.commit()


def test_pass_creates_device_and_claims_two_macs_from_the_pool(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    device = service.record_result(
        order_number="12345.6",
        serial_number="EM20260001",
        operator="4521",
        test_result="PASS",
        notes="",
        mac1="AA:BB:CC:DD:EE:00",
    )

    assert device.used is True
    assert device.ethaddr_id == "AA:BB:CC:DD:EE:00"
    # MAC2 is the next available pool entry, excluding MAC1.
    assert device.eth1addr_id == "AA:BB:CC:DD:EE:01"

    pool = {m.mac_address: m.used for m in session.query(MACAddressPool).all()}
    assert pool["AA:BB:CC:DD:EE:00"] is True
    assert pool["AA:BB:CC:DD:EE:01"] is True
    assert pool["AA:BB:CC:DD:EE:02"] is False


def test_fail_creates_device_with_no_macs_and_a_failure_note(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    device = service.record_result(
        order_number="12345.6",
        serial_number="EM20260001",
        operator="4521",
        test_result="FAIL",
        notes="fails -LL during functional test",
    )

    assert device.used is False
    assert device.ethaddr_id is None
    assert device.eth1addr_id is None
    assert len(device.failure_notes) == 1
    assert device.failure_notes[0].reason == "fails -LL during functional test"

    # A FAIL never touches the MAC pool.
    assert all(not m.used for m in session.query(MACAddressPool).all())


def test_retest_fail_then_fail_appends_a_second_failure_note(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        test_result="FAIL", notes="fails -LL",
    )
    device = service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4522",
        test_result="FAIL", notes="fails -LL again after rework",
    )

    assert session.query(Device).count() == 1
    assert [note.reason for note in device.failure_notes] == [
        "fails -LL",
        "fails -LL again after rework",
    ]


def test_retest_fail_then_pass_reuses_the_same_row_and_claims_macs(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    first = service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        test_result="FAIL", notes="fails -LL",
    )
    second = service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4522",
        test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:00",
    )

    assert session.query(Device).count() == 1
    assert second.id == first.id
    assert second.test_result == "PASS"
    assert second.used is True
    assert second.ethaddr_id == "AA:BB:CC:DD:EE:00"
    # The failure history from the earlier attempt is preserved.
    assert len(second.failure_notes) == 1


def test_recording_against_an_already_passed_serial_is_rejected(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:00",
    )

    with pytest.raises(ValueError, match="already passed"):
        service.record_result(
            order_number="12345.6", serial_number="EM20260001", operator="4522",
            test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:02",
        )


def test_pass_rejects_a_mac1_not_in_the_pool(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    with pytest.raises(ValueError, match="not available"):
        service.record_result(
            order_number="12345.6", serial_number="EM20260001", operator="4521",
            test_result="PASS", notes="", mac1="FF:FF:FF:FF:FF:FF",
        )


def test_pass_rejects_a_mac1_already_used_by_another_device(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:00",
    )

    with pytest.raises(ValueError, match="not available"):
        service.record_result(
            order_number="12345.6", serial_number="EM20260002", operator="4521",
            test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:00",
        )


def test_pass_raises_when_the_pool_has_no_second_address_available(session):
    seed_order_and_pool(session, mac_count=1)
    service = DeviceService(session)

    with pytest.raises(ValueError, match="second MAC"):
        service.record_result(
            order_number="12345.6", serial_number="EM20260001", operator="4521",
            test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:00",
        )