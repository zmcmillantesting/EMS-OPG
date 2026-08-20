import pytest

from ems_opg.database.models import Device, Order
from ems_opg.services.device_service import DeviceService
from ems_opg.services.order_service import OrderService


def test_create_order_success(session):
    order = OrderService(session).create_order("12345.6", 10)

    assert order.id is not None
    assert order.order_number == "12345.6"
    assert order.quantity == 10


@pytest.mark.parametrize("bad_number", ["123.4", "abcde.6", "12345", "12345.67"])
def test_create_order_rejects_bad_format(session, bad_number):
    with pytest.raises(ValueError, match="formatted as"):
        OrderService(session).create_order(bad_number, 10)


def test_create_order_rejects_quantity_below_one(session):
    with pytest.raises(ValueError, match="at least 1"):
        OrderService(session).create_order("12345.6", 0)


def test_create_order_rejects_duplicate_order_number(session):
    service = OrderService(session)
    service.create_order("12345.6", 10)

    with pytest.raises(ValueError, match="already exists"):
        service.create_order("12345.6", 5)


def test_correct_order_renames_and_cascades_to_devices(session):
    service = OrderService(session)
    service.create_order("12345.6", 10)
    session.add(Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"))
    session.commit()

    order = service.correct_order("12345.6", new_order_number="99999.1")

    assert order.order_number == "99999.1"
    device = session.query(Device).filter_by(serial_number="EM20260001").one()
    assert device.order_number == "99999.1"


def test_correct_order_changes_quantity(session):
    service = OrderService(session)
    service.create_order("12345.6", 10)

    order = service.correct_order("12345.6", quantity=20)

    assert order.quantity == 20


def test_correct_order_rejects_quantity_below_current_passed_count(session):
    order_service = OrderService(session)
    order_service.create_order("12345.6", 10)

    device_service = DeviceService(session)
    from ems_opg.database.models import MACAddressPool
    session.add_all([
        MACAddressPool(mac_address="AA:BB:CC:DD:EE:00"),
        MACAddressPool(mac_address="AA:BB:CC:DD:EE:01"),
    ])
    session.commit()
    device_service.record_result(
        order_number="12345.6", serial_number="EM20260001", operator="4521",
        test_result="PASS", notes="", mac1="AA:BB:CC:DD:EE:00",
    )

    with pytest.raises(ValueError, match="already passed"):
        order_service.correct_order("12345.6", quantity=0)


def test_correct_order_rejects_rename_to_an_existing_order_number(session):
    service = OrderService(session)
    service.create_order("12345.6", 10)
    service.create_order("99999.1", 5)

    with pytest.raises(ValueError, match="already exists"):
        service.correct_order("12345.6", new_order_number="99999.1")


def test_correct_order_raises_for_unknown_order(session):
    with pytest.raises(ValueError, match="not found"):
        OrderService(session).correct_order("00000.0", quantity=5)