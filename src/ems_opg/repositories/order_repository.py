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
    
    def list_all_orders(self):
        return self.session.scalars(
            select(Order)
        ).all()
    
    def create(self, order):
        if self.get_by_order_number(order.order_number):
            raise ValueError(
                f"Order with order_number {order.order_number} already exists."
            )
        self.session.add(order)

    def update(self):
        self.session.commit()

    def delete(self, order):
        self.session.delete(order)
        self.session.flush()


    