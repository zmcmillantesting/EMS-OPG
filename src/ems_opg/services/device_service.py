from datetime import UTC, datetime

from ems_opg.database.models import Device, DeviceFailureNote
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.mac_address_repository import MacAddressRepository


class DeviceService:

    def __init__(self, session):
        self.session = session
        self.repository = DeviceRepository(session)
        self.macs = MacAddressRepository(session)

    def record_result(
        self,
        order_number,
        serial_number,
        operator,
        test_result,
        notes,
        mac1=None,
    ):
        """
        Save a completed test session as a Device row. Serial+order is
        the device's identity, assigned before testing even starts, so
        this is an upsert rather than a plain insert: a serial that
        previously failed and is being retested reuses its existing row
        instead of creating a new one. A serial that already passed can't
        be re-recorded.

        mac1 is required (MAC2 is auto-assigned from the pool) only when
        test_result == "PASS" - a FAIL never touches the MAC pool.
        """

        existing = self.repository.get_by_order_and_serial(order_number, serial_number)

        if existing is not None and existing.test_result == "PASS":
            raise ValueError(
                f"Serial {serial_number} in order {order_number} has "
                "already passed testing."
            )

        device = existing or Device(
            order_number=order_number,
            serial_number=serial_number,
        )

        device.operator = operator
        device.test_result = test_result
        device.timestamp = datetime.now(UTC)

        if test_result == "PASS":
            mac_entry_1 = self.macs.get_by_mac(mac1)
            if mac_entry_1 is None or mac_entry_1.used:
                raise ValueError(f"MAC address {mac1} is not available.")

            mac_entry_2 = self.macs.get_next_available_excluding(mac1)
            if mac_entry_2 is None:
                raise ValueError("No second MAC address available in the pool.")

            device.ethaddr_id = mac_entry_1.mac_address
            device.eth1addr_id = mac_entry_2.mac_address
            device.used = True

            self.macs.mark_used(mac_entry_1)
            self.macs.mark_used(mac_entry_2)
        else:
            device.used = False
            # MACs are left exactly as they are (null, on a first
            # failure) - a FAIL never claims or releases pool addresses.

        if existing is None:
            self.repository.create(device)

        self.session.flush()  # device.id must exist before the note below

        if test_result == "FAIL":
            device.failure_notes.append(DeviceFailureNote(
                operator=operator,
                reason=notes,
            ))

        self.session.commit()
        return device