from ems_opg.database.models import Order


def test_create_order(session):

    order = Order(
        order_number="SO-1001",
        part_number="FIN-001",
        status="Open",
    )

    session.add(order)
    session.commit()

    assert order.id is not None
    assert order.order_number == "SO-1001"
    assert order.status == "Open"


def test_query_order(session):

    order = Order(
        order_number="SO-2000",
        part_number="FIN-500",
        status="Closed",
    )

    session.add(order)
    session.commit()

    db_order = (
        session.query(Order)
        .filter_by(order_number="SO-2000")
        .first()
    )

    assert db_order is not None
    assert db_order.status == "Closed"