from datetime import UTC, datetime

from sqlalchemy import select

from ems_opg.database.models import Device, Order

class DeviceRepository:

    def __init__(self, session):
        self.session = session

    def get_by_mac(self, ethaddr, ethaddr1):
        return self.session.scalar(
            select(Device)
            .where(Device.ethaddr_id == ethaddr)
            .where(Device.ethaddr1_id == ethaddr1)
        )

    def get_by_serial(self, serial):

        return self.session.scalar(
            select(Device).where(
                Device.serial_number == serial
            )
        )

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

        return self.session.scalar(
            select(Device).where(
                Device.id == device.id
            )
        ).all()
    
    def get_by_order(self, order_number):

        return self.session.scalar(
            select(Device).where(
                Device.used == True
            )
        ).all()

    def list_available(self):
        return self.session.scalar(
            select(Device).where(Device.used == False)
        ).all()

    def assign_order(self, device, order, serial, operator):
        if device.used:
            raise ValueError("MAC address has already been used.")

        existing = self.get_by_serial(serial)
        if existing and existing.id != device.id:
            raise ValueError("Serial number already exists.")

        order_obj = self.session.scalar(
            select(Order).where(Order.order_number == order)
        )
        if order_obj is None:
            raise ValueError("Order not found.")

        device.order_number = order
        device.serial_number = serial
        device.operator = operator
        device.used = True
        device.timestamp = datetime.now(UTC)

        self.session.commit()
        return device
