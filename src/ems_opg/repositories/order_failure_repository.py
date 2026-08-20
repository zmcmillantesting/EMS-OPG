from sqlalchemy import select

from ems_opg.database.models import OrderFailure


class OrderFailureRepository:

    def __init__(self, session):
        self.session = session

    def create(self, failure):
        self.session.add(failure)
        return failure

    def list_by_order(self, order_number):
        return self.session.scalars(
            select(OrderFailure)
            .where(OrderFailure.order_number == order_number)
            .order_by(OrderFailure.timestamp)
        ).all()