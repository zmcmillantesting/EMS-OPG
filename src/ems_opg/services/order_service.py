from ems_opg.core.validators import is_valid_order_number
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
        if not is_valid_order_number(order_number):
            raise ValueError(
                "Order number must be formatted as 0000.0 or 00000.0 "
                "(4-5 digits, a decimal point, then exactly one digit)."
            )

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
        elif quantity > order.quantity:
            order.quantity = quantity

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

    def correct_order(self, order_number, new_order_number=None, quantity=None):
        """
        Rename an order's number and/or adjust its planned quantity without
        touching any device rows individually - for orders large enough
        that per-device correction isn't practical (a mistyped order
        number, or a quantity that needs adjusting after the fact).
        """

        order = self.orders.get_by_order_number(order_number)
        if order is None:
            raise ValueError(f"Order {order_number} not found.")

        devices = self.devices.list_by_order(order_number)
        removed_count = 0

        if quantity is not None:
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")

            finalized = [device for device in devices if device.used]
            if quantity < len(finalized):
                raise ValueError(
                    f"Cannot set quantity below {len(finalized)} - that many "
                    f"device(s) on this order are already finalized."
                )
            excess = len(devices) - quantity
            if excess > 0:
                # Shrinking below the current device count - trim the
                # most-recently-provisioned devices that were never
                # assigned to a physical unit, and release the MAC pair
                # each one was holding back to the pool. The finalized
                # check above guarantees there are at least `excess`
                # untested devices to remove.
                untested = sorted(
                    (device for device in devices if not device.used),
                    key=lambda device: device.id,
                    reverse=True,
                )
                to_remove = untested[:excess]

                for device in to_remove:
                    for mac_value in (device.ethaddr_id, device.eth1addr_id):
                        if not mac_value:
                            continue
                        mac_entry = self.macs.get_by_mac(mac_value)
                        if mac_entry is not None:
                            self.macs.mark_unused(mac_entry)
                    self.devices.delete(device)

                removed_count = len(to_remove)
                removed_ids = {device.id for device in to_remove}
                devices = [device for device in devices if device.id not in removed_ids]

            order.quantity = quantity

        if new_order_number and new_order_number != order_number:
            if not is_valid_order_number(new_order_number):
                raise ValueError(
                    "Order number must be formatted as 0000.0 or 00000.0 "
                    "(4-5 digits, a decimal point, then exactly one digit)."
                )

            if self.orders.get_by_order_number(new_order_number) is not None:
                raise ValueError(f"Order {new_order_number} already exists.")

            order.order_number = new_order_number
            for device in devices:
                device.order_number = new_order_number

        self.session.flush()
        return order, removed_count

