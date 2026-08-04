from ems_opg.database.models import Device, Order


def test_create_device(session):

    order = Order(
        order_number="SO-100",
        part_number="ABC",
        status="Open",
    )

    session.add(order)
    session.commit()

    device = Device(
        order_number=order.order_number,
        serial_number="SN001",
        ethaddr_id="00:11:22:33:44:55",
        ethaddr1_id="00:11:22:33:44:56",
        used=True,
        test_result="Pass",
        operator="Tester",
    )

    session.add(device)
    session.commit()

    assert device.id is not None
    assert device.test_result == "Pass"


def test_update_device(session):

    order = Order(
        order_number="SO-101",
        part_number="ABC",
        status="Open",
    )

    session.add(order)
    session.commit()

    device = Device(
        order_number=order.order_number,
        serial_number="SN002",
        ethaddr_id="00:11:22:33:44:56",
        ethaddr1_id="00:11:22:33:44:57",
        used=False,
        test_result="Fail",
        operator="Tester",
    )

    session.add(device)
    session.commit()

    device.test_result = "Pass"
    session.commit()

    assert device.test_result == "Pass"


def test_assign_order_to_device(session):

    from ems_opg.repositories.device_repository import DeviceRepository
    from ems_opg.services.device_service import DeviceService

    order = Order(
        order_number="SO-200",
        part_number="XYZ",
        status="Open",
    )

    session.add(order)
    session.commit()

    device = Device(
        order_number=order.order_number,
        serial_number="SN003",
        ethaddr_id="00:11:22:33:44:57",
        ethaddr1_id="00:11:22:33:44:58",
        used=False,
        test_result="Pending",
        operator="Importer",
    )

    session.add(device)
    session.commit()

    service = DeviceService(session)
    reserved = service.reserve_device(
        ethaddr_id=device.ethaddr_id,
        ethaddr1_id=device.ethaddr1_id,
        order_number=order.order_number,
        serial_number="SN003-ASSIGNED",
        operator="Technician",
    )

    assert reserved.used is True
    assert reserved.operator == "Technician"
    assert reserved.serial_number == "SN003-ASSIGNED"
    assert reserved.order_number == order.order_number
