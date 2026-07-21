from sqlalchemy import select

from ems_opg.database.models import Order

class OrderRepository:

    def __init__(self, session):
        self.session = session

    def get_by_order_number(self, order_number):
        return self.session.scalar(
            select(Order).where(
                Order.order_number == order_number
            )
        )
    
    def create(self, order):
        self.session.add(order)
        self.session.commit()

    def update(self):
        self.session.commit()

    def delete(self, order):
        self.session.delete(order)
        self.session.commit()


    