from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ems_opg.database.base import Base
from ems_opg.database.models import Device, Order
from ems_opg.services.device_service import DeviceService


def test_reserve_device_end_to_end():
    """
    Verify that:
        Order -> DeviceService -> DeviceRepository -> Database
    all communicate correctly.
    """

    # In-memory database
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    session = Session()

    # Create an order
    order = Order(
        order_number="100001",
        part_number="PN-001",
        quantity=1,
    )

    session.add(order)

    # Create an unused device
    device = Device(
        order_number="100001",
        serial_number="",
        ethaddr_id=1,
        eth1addr_id=2,
        operator="",
        test_result="",
        used=False,
    )

    session.add(device)

    session.commit()

    # Service under test
    service = DeviceService(session)

    reserved = service.reserve_device(
        ethaddr_id=1,
        eth1addr_id=2,
        order_number="100001",
        serial_number="SER123456",
        operator="Zach",
    )

    assert reserved.used is True
    assert reserved.serial_number == "SER123456"
    assert reserved.operator == "Zach"
    assert reserved.order_number == "100001"