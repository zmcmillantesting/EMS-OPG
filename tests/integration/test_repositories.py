from ems_opg.database.models import Device, MACAddressPool, Order
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.mac_address_repository import MacAddressRepository


def test_count_passed_by_order_only_counts_pass(session):
    session.add(Order(order_number="12345.6", quantity=5))
    session.add_all([
        Device(order_number="12345.6", serial_number="EM20260001", test_result="PASS", operator="4521", used=True),
        Device(order_number="12345.6", serial_number="EM20260002", test_result="FAIL", operator="4521"),
        Device(order_number="12345.6", serial_number="EM20260003", test_result="PASS", operator="4521", used=True),
    ])
    session.commit()

    assert DeviceRepository(session).count_passed_by_order("12345.6") == 2


def test_get_next_available_excluding_skips_the_given_mac(session):
    session.add_all([
        MACAddressPool(mac_address="AA:BB:CC:DD:EE:00"),
        MACAddressPool(mac_address="AA:BB:CC:DD:EE:01"),
    ])
    session.commit()

    repo = MacAddressRepository(session)
    result = repo.get_next_available_excluding("AA:BB:CC:DD:EE:00")

    assert result.mac_address == "AA:BB:CC:DD:EE:01"


def test_get_next_available_excluding_returns_none_when_nothing_else_left(session):
    session.add(MACAddressPool(mac_address="AA:BB:CC:DD:EE:00"))
    session.commit()

    repo = MacAddressRepository(session)
    assert repo.get_next_available_excluding("AA:BB:CC:DD:EE:00") is None


def test_get_by_order_and_serial_disambiguates_same_serial_across_orders(session):
    session.add_all([
        Order(order_number="12345.6", quantity=5),
        Order(order_number="99999.1", quantity=5),
    ])
    session.add_all([
        Device(order_number="12345.6", serial_number="EM20260001", test_result="FAIL", operator="4521"),
        Device(order_number="99999.1", serial_number="EM20260001", test_result="PASS", operator="4522", used=True),
    ])
    session.commit()

    repo = DeviceRepository(session)
    assert repo.get_by_order_and_serial("12345.6", "EM20260001").test_result == "FAIL"
    assert repo.get_by_order_and_serial("99999.1", "EM20260001").test_result == "PASS"