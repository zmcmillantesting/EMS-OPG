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
        first_mac_address="00:11:22:33:44:55",
        second_mac_address="00:11:22:33:44:56",
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
        first_mac_address="00:11:22:33:44:56",
        second_mac_address="00:11:22:33:44:57",
        used=False,
        test_result="Fail",
        operator="Tester",
    )

    session.add(device)
    session.commit()

    device.test_result = "Pass"
    session.commit()

    assert device.test_result == "Pass"