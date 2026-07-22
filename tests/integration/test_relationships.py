from ems_opg.database.models import Device, Order


def test_order_has_devices(session):

    order = Order(
        order_number="SO-300",
        part_number="XYZ",
        status="Open",
    )

    session.add(order)
    session.commit()

    session.add_all([
        Device(
            order_number=order.order_number,
            serial_number="SN1",
            first_mac_address="00:11:22:33:44:01",
            second_mac_address="00:11:22:33:44:02",
            used=True,
            test_result="Pass",
            operator="Tester",
        ),
        Device(
            order_number=order.order_number,
            serial_number="SN2",
            first_mac_address="00:11:22:33:44:02",
            second_mac_address="00:11:22:33:44:03",
            used=True,
            test_result="Pass",
            operator="Tester",
        ),
    ])

    session.commit()

    assert len(order.devices) == 2