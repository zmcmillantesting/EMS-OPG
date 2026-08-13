from datetime import UTC, datetime

from sqlalchemy import or_, select

from ems_opg.database.models import Device, Order

class DeviceRepository:

    def __init__(self, session):
        self.session = session

    def get_by_mac(self, ethaddr, eth1addr):
        return self.session.scalar(
            select(Device)
            .where(Device.ethaddr_id == ethaddr)
            .where(Device.eth1addr_id == eth1addr)
        )

    def get_by_serial(self, serial):
        return self.session.scalar(
            select(Device).where(
                Device.serial_number == serial
            )
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

    def mark_used(self, device):
        device.used = True
        return device
    
    def mark_unused(self, device):
        device.used = False
        return device
    
    def get_by_order(self, order_number):

        return self.session.scalars(
            select(Device).where(
                Device.used == True
            )
            .where(Device.order_number == order_number)
        ).all()

    def list_by_order(self, order_number):
        return self.session.scalars(
            select(Device).where(Device.order_number == order_number)
        ).all()

    def list_available(self):
        return self.session.scalars(
            select(Device).where(Device.used.is_(False))
        ).all()

    def assign_order(self, device, order_number, serial_number, operator, test_result):
        if device.used:
            raise ValueError("MAC address has already been used.")

        existing = self.get_by_serial(serial_number)
        if existing and existing.id != device.id:
            raise ValueError("Serial number already exists.")

        order_obj = self.session.scalars(
            select(Order).where(Order.order_number == order_number)
        ).all()
        if not order_obj:
            raise ValueError("Order not found.")

        device.order_number = order_number
        device.serial_number = serial_number
        device.operator = operator
        device.test_result = test_result
        device.used = True
        device.timestamp = datetime.now(UTC)

        self.session.commit()
        return device
