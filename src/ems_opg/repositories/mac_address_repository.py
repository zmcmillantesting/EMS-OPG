from sqlalchemy import select

from ems_opg.database.models import MACAddressPool

class MacAddressRepository:

    def __init__(self, session):
        self.session = session

    def get_by_id(self, mac_id):

        return self.session.get(MACAddressPool, mac_id)

    def get_by_mac(self, mac_address):
        return self.session.scalar(
            select(MACAddressPool).where(
                MACAddressPool.mac_address == mac_address
            )
        )

    def list_all(self):

        return (
            self.session.scalars(
                select(MACAddressPool).order_by(MACAddressPool.mac_address)
            )
            .all()
        )

    def list_available(self):

        return (
            self.session.scalars(
                select(MACAddressPool)
                .where(MACAddressPool.used.is_(False))
                .order_by(MACAddressPool.mac_address)
            )
            .all()
        )
    
    def get_next_available(self):
        return self.session.scalar(
            select(MACAddressPool)
            .where(MACAddressPool.used.is_(False))
            .order_by(MACAddressPool.mac_address)
        )

    def mark_used(self, mac):
        mac.used = True

    def mark_unused(self, mac):
        mac.used = False

    def create(self, mac):
        self.session.add(mac)

    def commit(self):
        self.session.commit()

    def delete(self, mac):
        self.session.delete(mac)

    def rollback(self):
        self.session.rollback()

    def exists(self, mac_address):
        return self.get_by_mac(mac_address) is not None