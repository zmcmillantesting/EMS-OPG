from ems_opg.repositories.device_repository import DeviceRepository


class DeviceService:

    def __init__(self, session):

        self.repository = DeviceRepository(session)

    def reserve_device(
        self,
        ethaddr_id,
        ethaddr1_id,
        order_number,
        serial_number,
        operator,
    ):

        device = self.repository.get_by_mac(ethaddr_id, ethaddr1_id)

        if device is None:

            raise ValueError(
                "MAC address not found."
            )

        if device.used:
            raise ValueError("MAC address has already been used.")

        self.repository.assign_order(
            device,
            order_number,
            serial_number,
            operator,
        )

        return device