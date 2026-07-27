from sqlalchemy import select

from ems_opg.database.models import AuditLog


class AuditRepository:

    def __init__(self, session):
        self.session = session

    def create(self, audit_log):
        self.session.add(audit_log)
        self.session.commit()
        return audit_log

    def get_by_id(self, audit_id):
        return self.session.get(AuditLog, audit_id)

    def list_all(self):
        return self.session.scalars(select(AuditLog)).all()

    def get_by_action(self, action):
        return self.session.scalars(
            select(AuditLog).where(AuditLog.action == action)
        ).all()

    def update(self):
        self.session.commit()

    def delete(self, audit_log):
        self.session.delete(audit_log)
        self.session.commit()
