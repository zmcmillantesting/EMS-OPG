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


def test_record_pass_creates_device_and_claims_two_macs_from_the_pool(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    device = service.record_pass(
        order_number="12345.6",
        serial_number="EM20260001",
        operator="4521",
        mac1="AA:BB:CC:DD:EE:00",
    )

    assert device.used is True
    assert device.test_result == "PASS"
    assert device.ethaddr_id == "AA:BB:CC:DD:EE:00"
    # MAC2 is the next available pool entry, excluding MAC1.
    assert device.eth1addr_id == "AA:BB:CC:DD:EE:01"

    pool = {m.mac_address: m.used for m in session.query(MACAddressPool).all()}
    assert pool["AA:BB:CC:DD:EE:00"] is True
    assert pool["AA:BB:CC:DD:EE:01"] is True
    assert pool["AA:BB:CC:DD:EE:02"] is False


def test_record_pass_rejects_a_duplicate_serial_for_the_same_order(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    service.record_pass(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        mac1="AA:BB:CC:DD:EE:00",
    )

    with pytest.raises(ValueError, match="already exists"):
        service.record_pass(
            order_number="12345.6", serial_number="EM20260001", operator="4522",
            mac1="AA:BB:CC:DD:EE:02",
        )

    assert session.query(Device).count() == 1


def test_record_pass_rejects_a_mac1_not_in_the_pool(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    with pytest.raises(ValueError, match="not available"):
        service.record_pass(
            order_number="12345.6", serial_number="EM20260001", operator="4521",
            mac1="FF:FF:FF:FF:FF:FF",
        )


def test_record_pass_rejects_a_mac1_already_used_by_another_device(session):
    seed_order_and_pool(session)
    service = DeviceService(session)

    service.record_pass(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        mac1="AA:BB:CC:DD:EE:00",
    )

    with pytest.raises(ValueError, match="not available"):
        service.record_pass(
            order_number="12345.6", serial_number="EM20260002", operator="4521",
            mac1="AA:BB:CC:DD:EE:00",
        )


def test_record_pass_raises_when_the_pool_has_no_second_address_available(session):
    seed_order_and_pool(session, mac_count=1)
    service = DeviceService(session)

    with pytest.raises(ValueError, match="second MAC"):
        service.record_pass(
            order_number="12345.6", serial_number="EM20260001", operator="4521",
            mac1="AA:BB:CC:DD:EE:00",
        )