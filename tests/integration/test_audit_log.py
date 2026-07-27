from ems_opg.database.models import AuditLog
from ems_opg.repositories.audit_repository import AuditRepository


def test_create_audit_log(session):
    repository = AuditRepository(session)

    log = AuditLog(
        operator="Tester",
        action="Created Order",
        details="Testing audit logging",
    )

    created_log = repository.create(log)

    assert created_log.id is not None
    assert created_log.action == "Created Order"
    assert repository.get_by_id(created_log.id) is not None
    assert repository.get_by_action("Created Order")[0].id == created_log.id