import pytest
from sqlalchemy.exc import IntegrityError

from ems_opg.database.models import Device, MACAddressPool, Order


def test_create_order_with_quantity_only(session):
    order = Order(order_number="12345.6", quantity=10)

    session.add(order)
    session.commit()

    assert order.id is not None
    assert order.status == "Open"
    assert order.quantity == 10


def test_order_number_is_unique(session):
    session.add(Order(order_number="12345.6", quantity=5))
    session.commit()

    session.add(Order(order_number="12345.6", quantity=5))
    with pytest.raises(IntegrityError):
        session.commit()


def test_order_has_devices_relationship(session):
    order = Order(order_number="12345.6", quantity=5)
    session.add(order)
    session.commit()

    session.add_all([
        Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"),
        Device(order_number="12345.6", serial_number="EM20260002", test_result="FAIL", operator="4521"),
    ])
    session.commit()

    assert len(order.devices) == 2


def test_device_with_no_macs_is_valid_for_a_failed_test(session):
    session.add(Order(order_number="12345.6", quantity=5))
    session.commit()

    device = Device(
        order_number="12345.6",
        serial_number="EM20260001",
        test_result="FAIL",
        operator="4521",
        used=False,
    )
    session.add(device)
    session.commit()

    assert device.ethaddr_id is None
    assert device.eth1addr_id is None


def test_same_serial_allowed_across_different_orders(session):
    session.add_all([
        Order(order_number="12345.6", quantity=5),
        Order(order_number="99999.1", quantity=5),
    ])
    session.commit()

    session.add_all([
        Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"),
        Device(order_number="99999.1", serial_number="EM20260001", test_result="FAIL", operator="4521"),
    ])
    session.commit()

    assert session.query(Device).count() == 2


def test_duplicate_serial_within_same_order_is_rejected(session):
    session.add(Order(order_number="12345.6", quantity=5))
    session.commit()

    session.add(Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"))
    session.commit()

    session.add(Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_duplicate_mac_across_devices_is_rejected(session):
    session.add(Order(order_number="12345.6", quantity=5))
    session.commit()

    session.add(Device(
        order_number="12345.6", serial_number="EM20260001", test_result="PASS", operator="4521",
        used=True, ethaddr_id="AA:BB:CC:DD:EE:01", eth1addr_id="AA:BB:CC:DD:EE:02",
    ))
    session.commit()

    session.add(Device(
        order_number="12345.6", serial_number="EM20260002", test_result="PASS", operator="4521",
        used=True, ethaddr_id="AA:BB:CC:DD:EE:01", eth1addr_id="AA:BB:CC:DD:EE:03",
    ))
    with pytest.raises(IntegrityError):
        session.commit()


def test_two_devices_can_both_have_null_macs(session):
    """A unique index still permits multiple NULLs - two FAILed devices
    with no MACs shouldn't collide with each other."""
    session.add(Order(order_number="12345.6", quantity=5))
    session.commit()

    session.add_all([
        Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"),
        Device(order_number="12345.6", serial_number="EM20260002", test_result="FAIL", operator="4521"),
    ])
    session.commit()

    assert session.query(Device).count() == 2


def test_mac_address_pool_entries_are_unique(session):
    session.add(MACAddressPool(mac_address="AA:BB:CC:DD:EE:01"))
    session.commit()

    session.add(MACAddressPool(mac_address="AA:BB:CC:DD:EE:01"))
    with pytest.raises(IntegrityError):
        session.commit()

def test_order_failures_accumulate_and_stay_ordered(session):
    from ems_opg.database.models import OrderFailure

    order = Order(order_number="12345.6", quantity=5)
    session.add(order)
    session.commit()

    order.failures.append(OrderFailure(operator="4521", reason="fails -LL"))
    order.failures.append(OrderFailure(operator="4522", reason="fails -LL again"))
    session.commit()

    assert [f.reason for f in order.failures] == ["fails -LL", "fails -LL again"]


def test_device_with_null_macs_is_a_valid_row_at_the_schema_level(session):
    """
    The app itself never creates a Device with null MACs anymore (every
    Device row is a PASS by construction), but the columns stay nullable
    at the schema level - e.g. the historical backfill scripts insert
    rows directly without going through DeviceService.
    """
    session.add(Order(order_number="12345.6", quantity=5))
    session.commit()

    device = Device(order_number="12345.6", serial_number="EM20260001", operator="4521")
    session.add(device)
    session.commit()

    assert device.ethaddr_id is None
    assert device.eth1addr_id is None