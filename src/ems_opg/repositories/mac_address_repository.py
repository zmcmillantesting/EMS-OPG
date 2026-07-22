from sqlalchemy import select

from ems_opg.database.models import MacAddressPool

class MacAddressRepository:

    def __init__(self, session):
        self.session = session

    def get_by_id(self, mac_id):

        return self.session.get(MacAddressPool, mac_id)

    def get_by_mac(self, mac_address):
        return self.session.scalar(
            select(MacAddressPool).where(
                MacAddressPool.mac_address == mac_address
            )
        )

    def list_all(self):

        return (
            self.session.scalars(
                select(MacAddressPool).order_by(MacAddressPool.mac_address)
            )
            .all()
        )

    def list_available(self):

        return (
            self.session.scalars(
                select(MacAddressPool)
                .where(MacAddressPool.used.is_(False))
                .order_by(MacAddressPool.mac_address)
            )
            .all()
        )

    def get_first_available(self):

        return self.session.scalar(
                select(MacAddressPool)
                .where(MacAddressPool.used.is_(False))
                .order_by(MacAddressPool.mac_address)
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