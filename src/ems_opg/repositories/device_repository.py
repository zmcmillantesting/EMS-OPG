from sqlalchemy import func, or_, select

from ems_opg.database.models import Device

class DeviceRepository:

    def __init__(self, session):
        self.session = session

    def get_by_mac(self, ethaddr, eth1addr):
        return self.session.scalar(
            select(Device)
            .where(Device.ethaddr_id == ethaddr)
            .where(Device.eth1addr_id == eth1addr)
        )

    def list_by_serial(self, serial):
        """
        Serial numbers are only unique within an order, so a bare serial
        can match devices across multiple orders - callers that need a
        single device must disambiguate by order (see
        get_by_order_and_serial) or handle multiple results themselves.
        """
        return self.session.scalars(
            select(Device).where(Device.serial_number == serial)
        ).all()

    def get_by_order_and_serial(self, order_number, serial):
        return self.session.scalar(
            select(Device)
            .where(Device.order_number == order_number)
            .where(Device.serial_number == serial)
        )

    def get_by_single_mac(self, mac):
        return self.session.scalar(
            select(Device).where(
                or_(
                    Device.ethaddr_id == mac,
                    Device.eth1addr_id == mac,
                )
            )
        )

    def list_all(self):
        return self.session.scalars(
            select(Device).order_by(Device.timestamp.desc())
        ).all()

    def search(self, query):
        pattern = f"%{query.lower()}%"
        return self.session.scalars(
            select(Device)
            .where(
                or_(
                    Device.order_number.ilike(pattern),
                    Device.serial_number.ilike(pattern),
                    Device.ethaddr_id.ilike(pattern),
                    Device.eth1addr_id.ilike(pattern),
                    Device.operator.ilike(pattern),
                    Device.test_result.ilike(pattern),
                )
            )
            .order_by(Device.timestamp.desc())
        ).all()

    def create(self, device):
        self.session.add(device)

    def update(self):
        self.session.commit()

    def delete(self, device):
        self.session.delete(device)

    def list_by_order(self, order_number):
        return self.session.scalars(
            select(Device).where(Device.order_number == order_number)
        ).all()

    def count_passed_by_order(self, order_number):
        """
        The "completed" side of an order's progress tracker - compared
        against Order.quantity for remaining = quantity - this count.
        Only PASS counts; a device sitting on a FAIL still needs a
        retest before it contributes.
        """
        return self.session.scalar(
            select(func.count(Device.id))
            .where(Device.order_number == order_number)
            .where(Device.test_result == "PASS")
        )