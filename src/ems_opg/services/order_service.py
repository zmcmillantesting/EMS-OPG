from ems_opg.core.validators import is_valid_order_number
from ems_opg.database.models import Order
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.order_repository import OrderRepository


class OrderService:

    def __init__(self, session):
        self.session = session
        self.orders = OrderRepository(session)
        self.devices = DeviceRepository(session)

    def create_order(self, order_number, quantity):
        """
        Replaces the old provision_order flow. Orders are no longer
        pre-loaded with MAC-claimed device rows - this just registers the
        order number and its target quantity so it shows up in the
        operator's order dropdown. Devices are created lazily, one at a
        time, as each serial number finishes testing.
        """

        if not is_valid_order_number(order_number):
            raise ValueError(
                "Order number must be formatted as 0000.0 or 00000.0 "
                "(4-5 digits, a decimal point, then exactly one digit)."
            )

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if self.orders.get_by_order_number(order_number) is not None:
            raise ValueError(f"Order {order_number} already exists.")

        order = Order(order_number=order_number, quantity=quantity)
        self.orders.create(order)
        self.session.commit()

        return order

    def correct_order(self, order_number, new_order_number=None, quantity=None):
        """
        Rename an order's number and/or adjust its target quantity.
        Unlike the old version of this method, there's no device
        trimming or MAC releasing to do - quantity is just a number used
        for progress reporting now, not a count of pre-created rows.
        """

        order = self.orders.get_by_order_number(order_number)
        if order is None:
            raise ValueError(f"Order {order_number} not found.")

        if quantity is not None:
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")

            passed = self.devices.count_passed_by_order(order_number)
            if quantity < passed:
                raise ValueError(
                    f"Cannot set quantity below {passed} - that many "
                    "device(s) on this order have already passed testing."
                )

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
            for device in self.devices.list_by_order(order_number):
                device.order_number = new_order_number

        self.session.flush()
        return order
    
    def record_failure(self, order_number, operator, reason):
        """
        Logs a failed test attempt against the order - no device, serial,
        or MAC involved. See OrderFailure on the Order model.
        """

        from ems_opg.database.models import OrderFailure
        from ems_opg.repositories.order_failure_repository import OrderFailureRepository

        order = self.orders.get_by_order_number(order_number)
        if order is None:
            raise ValueError(f"Order {order_number} not found.")

        failure = OrderFailure(
            order_number=order_number,
            operator=operator,
            reason=reason,
        )
        OrderFailureRepository(self.session).create(failure)
        self.session.commit()
        return failure