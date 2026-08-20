from datetime import UTC, datetime

from ems_opg.database.models import Device
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.mac_address_repository import MacAddressRepository


class DeviceService:

    def __init__(self, session):
        self.session = session
        self.repository = DeviceRepository(session)
        self.macs = MacAddressRepository(session)

    def record_pass(self, order_number, serial_number, operator, mac1):
        """
        Every Device row is a PASS by construction now - a board's serial
        is only ever assigned once it's already known good, so there's no
        upsert/retest concept here anymore. Rejects only on a genuine
        duplicate (the same serial entered twice for this order), not on
        "already tested" - retesting a failed board just runs it through
        the whole flow again with a fresh serial.
        """

        existing = self.repository.get_by_order_and_serial(order_number, serial_number)
        if existing is not None:
            raise ValueError(
                f"Serial {serial_number} already exists for order {order_number}."
            )

        mac_entry_1 = self.macs.get_by_mac(mac1)
        if mac_entry_1 is None or mac_entry_1.used:
            raise ValueError(f"MAC address {mac1} is not available.")

        mac_entry_2 = self.macs.get_next_available_excluding(mac1)
        if mac_entry_2 is None:
            raise ValueError("No second MAC address available in the pool.")

        device = Device(
            order_number=order_number,
            serial_number=serial_number,
            operator=operator,
            test_result="PASS",
            used=True,
            ethaddr_id=mac_entry_1.mac_address,
            eth1addr_id=mac_entry_2.mac_address,
            timestamp=datetime.now(UTC),
        )

        self.macs.mark_used(mac_entry_1)
        self.macs.mark_used(mac_entry_2)

        self.repository.create(device)
        self.session.commit()
        return device