from sqlalchemy import select

from ems_opg.database.models import Device

class DeviceRepository:

    def __init__(self, session):
        self.session = session

    def get_by_mac(self, mac_address):

        return self.session.scalar(
            select(Device).where(
                Device.mac_address == mac_address
            )
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

    def asign_to_order(self, device, order_number, serial_number, operator):
        device.order_number = order_number
        device.serial_number = serial_number
        device.operator = operator
        device.used = True
    