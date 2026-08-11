from ems_opg.database.models import Device, Order
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.mac_address_repository import MacAddressRepository
from ems_opg.repositories.order_repository import OrderRepository


class OrderService:

    def __init__(self, session):
        self.session = session
        self.orders = OrderRepository(session)
        self.macs = MacAddressRepository(session)
        self.devices = DeviceRepository(session)

    def provision_order(self, order_number, part_number, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        order = self.orders.get_by_order_number(order_number)
        if order is None:
            order = Order(
                order_number=order_number,
                part_number=part_number,
                quantity=quantity,
            )
            self.orders.create(order)

        existing = self.devices.list_by_order(order_number)
        already_provisioned = len(existing)

        remaining = quantity - already_provisioned
        if remaining <= 0:
            return {
                "created": 0,
                "already_provisioned": already_provisioned,
                "message": (
                    f"Order {order_number} already has "
                    f"{already_provisioned} device(s) provisioned."
                ),
            }

        available = self.macs.list_available()
        macs_needed = remaining * 2

        if len(available) < macs_needed:
            raise ValueError(
                f"Not enough MAC addresses available. "
                f"Need {macs_needed}, have {len(available)}."
            )

        created = []
        for i in range(remaining):
            mac_a = available[i * 2]
            mac_b = available[i * 2 + 1]

            serial_placeholder = (
                f"PENDING-{order_number}-{already_provisioned + i + 1:03d}"
            )

            device = Device(
                order_number=order_number,
                serial_number=serial_placeholder,
                ethaddr_id=mac_a.mac_address,
                eth1addr_id=mac_b.mac_address,
                used=False,
                test_result="PENDING",
                operator="",
            )
            self.devices.create(device)

            self.macs.mark_used(mac_a)
            self.macs.mark_used(mac_b)

            created.append(device)

        self.session.commit()

        return {
            "created": len(created),
            "already_provisioned": already_provisioned,
            "message": f"Provisioned {len(created)} device(s) for order {order_number}.",
        }
