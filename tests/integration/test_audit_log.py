from ems_opg.database.models import AuditLog


def test_create_audit_log(session):

    log = AuditLog(
        operator="Tester",
        action="Created Order",
        details="Testing audit logging",
    )

    session.add(log)
    session.commit()

    assert log.id is not None
    assert log.action == "Created Order"