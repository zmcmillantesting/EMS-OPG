from ems_opg.database.models import MACAddressPool
from ems_opg.repositories.mac_address_repository import MacAddressRepository


def test_mac_repository(session):
    repository = MacAddressRepository(session)

    repository.create(MACAddressPool(mac_address="00:13:C6:13:3F:00"))
    repository.create(MACAddressPool(mac_address="00:13:C6:13:3F:01"))
    repository.commit()

    first_mac = repository.get_by_mac("00:13:C6:13:3F:00")
    second_mac = repository.get_by_mac("00:13:C6:13:3F:01")
    next_available = repository.get_next_available()

    assert first_mac is not None
    assert second_mac is not None
    assert next_available is not None
    assert next_available.mac_address == "00:13:C6:13:3F:00"
