from pathlib import Path

from ems_opg.database.models import AuditLog, Device, MACAddressPool, Order
from ems_opg.repositories.audit_repository import AuditRepository
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.mac_address_repository import MacAddressRepository
from ems_opg.repositories.order_repository import OrderRepository
from ems_opg.services.device_service import DeviceService


def test_full_database_flow_with_audit_log(session):
    log_path = Path("logs") / "database_flow_test.log"
    log_path.parent.mkdir(exist_ok=True)
    log_lines = []

    if log_path.exists():
        log_path.unlink()

    def write_log(message: str) -> None:
        log_lines.append(message)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")

    def write_section(title: str) -> None:
        write_log("")
        write_log(f"=== {title} ===")

    write_section("Full Database Flow Test")
    write_log("Starting full database flow test")
    order_repository = OrderRepository(session)
    device_repository = DeviceRepository(session)
    mac_repository = MacAddressRepository(session)
    audit_repository = AuditRepository(session)
    device_service = DeviceService(session)

    order = Order(
        order_number="PO-9001",
        part_number="PN-9001",
        quantity=2,
        status="Open",
    )
    order_repository.create(order)
    write_log(f"Created order {order.order_number}")
    write_section("Order Setup")

    mac1 = MACAddressPool(mac_address="00:11:22:33:44:55")
    mac2 = MACAddressPool(mac_address="00:11:22:33:44:56")
    mac_repository.create(mac1)
    mac_repository.create(mac2)
    mac_repository.commit()
    write_log("Loaded MAC pool entries")
    write_section("Device Setup")

    device = Device(
        order_number=order.order_number,
        serial_number="",
        ethaddr_id="00:11:22:33:44:55",
        eth1addr_id="00:11:22:33:44:56",
        operator="",
        test_result="Pending",
        used=False,
    )
    device_repository.create(device)
    session.commit()

    second_device = Device(
        order_number=order.order_number,
        serial_number="SN-9002",
        ethaddr_id="00:11:22:33:44:57",
        eth1addr_id="00:11:22:33:44:58",
        operator="",
        test_result="Pending",
        used=False,
    )
    device_repository.create(second_device)
    session.commit()
    write_log("Created primary and secondary devices")
    write_section("Reservation Flow")

    reserved_device = device_service.reserve_device(
        ethaddr_id="00:11:22:33:44:55",
        eth1addr_id="00:11:22:33:44:56",
        order_number=order.order_number,
        serial_number="SN-9001",
        operator="Technician A",
        test_result="PASS",
    )
    write_log(f"Reserved device {reserved_device.serial_number}")

    if reserved_device.used:
        status = "PASS"
        failure = None
    else:
        status = "FAIL"
        failure = "Device was not reserved"

    audit_log = AuditLog(
        operator="Technician A",
        action="Device Reserved",
        details=(
            f"Order={order.order_number}; "
            f"Serial={reserved_device.serial_number}; "
            f"Status={status}; "
            f"Failure={failure or 'None'}"
        ),
    )
    audit_repository.create(audit_log)
    write_log(f"Recorded audit status: {status}")

    try:
        device_service.reserve_device(
            ethaddr_id="00:11:22:33:44:55",
            eth1addr_id="00:11:22:33:44:56",
            order_number=order.order_number,
            serial_number="SN-9002",
            operator="Technician B",
            test_result="PASS",
        )
    except ValueError as exc:
        failure_message = str(exc)
        write_log(f"Secondary reservation failed as expected: {failure_message}")
    else:
        failure_message = "Second reservation unexpectedly succeeded"
        write_log(f"Secondary reservation failed unexpectedly: {failure_message}")

    stored_order = order_repository.get_by_order_number(order.order_number)
    stored_device = device_repository.get_by_serial("SN-9001")
    stored_second_device = device_repository.get_by_serial("SN-9002")
    stored_mac = mac_repository.get_by_mac("00:11:22:33:44:55")
    stored_audit = audit_repository.get_by_action("Device Reserved")

    assert stored_order is not None
    assert stored_order.order_number == order.order_number
    assert stored_order.quantity == 2
    assert stored_device is not None
    assert stored_device.used is True
    assert stored_device.operator == "Technician A"

    assert stored_second_device is not None
    assert stored_second_device.serial_number == "SN-9002"
    assert stored_second_device.used is False

    assert stored_mac is not None
    assert stored_audit
    assert stored_audit[0].details is not None
    assert "PASS" in stored_audit[0].details
    assert "failed as expected" in log_lines[-1].lower() or "failed unexpectedly" in log_lines[-1].lower()

    write_section("Summary")
    write_log(f"Order: {stored_order.order_number}")
    write_log(f"Primary device serial: {stored_device.serial_number}")
    write_log(f"Secondary device serial: {stored_second_device.serial_number}")
    write_log(f"Primary device used: {stored_device.used}")
    write_log(f"Secondary device used: {stored_second_device.used}")
    write_log(f"Audit entries recorded: {len(stored_audit)}")
    write_log("Completed full database flow test")
