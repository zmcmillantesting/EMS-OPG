import pytest
from sqlalchemy.exc import IntegrityError

from ems_opg.database.models import Device, Order


def test_duplicate_mac_fails(session):

    order = Order(
        order_number="SO-1",
        part_number="ABC",
        status="Open",
    )

    session.add(order)
    session.commit()

    session.add(Device(
        order_number=order.order_number,
        serial_number="SN1",
        ethaddr_id="AA:BB:CC:DD:EE:FF",
        ethaddr1_id="BB:CC:DD:EE:FF:AA",
        used=True,
        test_result="Pass",
        operator="Tester",
    ))

    session.commit()

    session.add(Device(
        order_number=order.order_number,
        serial_number="SN2",
        ethaddr_id="AA:BB:CC:DD:EE:FF",
        ethaddr1_id="CC:DD:EE:FF:AA:BB",
        used=True,
        test_result="Pass",
        operator="Tester",
    ))

    with pytest.raises(IntegrityError):
        session.commit()