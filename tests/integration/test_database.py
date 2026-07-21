from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ems_opg.database.engine import DATABASE_FILE
from src.ems_opg.database.init_db import init_database
from src.ems_opg.database.session import SessionLocal
from src.ems_opg.database.models import Order, Device, AuditLog


def print_header(title: str):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():

    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    print_header("Creating Database")
    init_database(force=True)

    session = SessionLocal()

    try:

        ###################################################
        # CREATE ORDER
        ###################################################

        print_header("Creating Order")

        order = Order(
            order_number="SO-10001",
            part_number="FIN-5000",
            status="Open",
            quantity=15,
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        print(f"Order ID = {order.id}")

        ###################################################
        # CREATE DEVICES
        ###################################################

        print_header("Creating Devices")

        device1 = Device(
            order_number=order.order_number,
            serial_number="SN000001",
            mac_address="00:11:22:33:44:55",
            used=True,
            test_result="Pass",
            operator="Zach",
        )

        device2 = Device(
            order_number=order.order_number,
            serial_number="SN000002",
            mac_address="00:11:22:33:44:56",
            used=True,
            test_result="Fail",
            operator="Zach",
        )

        session.add_all([device1, device2])
        session.commit()

        print("Devices created.")

        ###################################################
        # CREATE AUDIT ENTRY
        ###################################################

        print_header("Creating Audit Log")

        audit = AuditLog(
            operator="Zach",
            action="Created Test Data",
            details="Database testing script executed."
        )

        session.add(audit)
        session.commit()

        print("Audit log created.")

        ###################################################
        # READ ORDER
        ###################################################

        print_header("Reading Order")

        db_order = (
            session.query(Order)
            .filter_by(order_number="SO-10001")
            .first()
        )

        print(db_order)

        ###################################################
        # RELATIONSHIP TEST
        ###################################################

        print_header("Relationship Test")

        print(f"Order {db_order.order_number}")

        for device in db_order.devices:
            print(
                device.serial_number,
                device.mac_address,
                device.test_result,
            )

        ###################################################
        # UPDATE DEVICE
        ###################################################

        print_header("Updating Device")

        device = (
            session.query(Device)
            .filter_by(serial_number="SN000002")
            .first()
        )

        device.test_result = "Pass"
        device.post_test_changes = "Reprogrammed firmware"

        session.commit()

        print("Device updated.")

        ###################################################
        # VERIFY UPDATE
        ###################################################

        print_header("Verify Update")

        device = (
            session.query(Device)
            .filter_by(serial_number="SN000002")
            .first()
        )

        print(device.test_result)
        print(device.post_test_changes)

        ###################################################
        # LIST AUDIT LOGS
        ###################################################

        print_header("Audit Log")

        logs = session.query(AuditLog).all()

        for log in logs:
            print(
                log.timestamp,
                log.operator,
                log.action,
            )

        ###################################################
        # COUNT RECORDS
        ###################################################

        print_header("Database Summary")

        print(
            "Orders:",
            session.query(Order).count()
        )

        print(
            "Devices:",
            session.query(Device).count()
        )

        print(
            "Audit Logs:",
            session.query(AuditLog).count()
        )

        ###################################################
        # DELETE TEST DATA
        ###################################################

        print_header("Cleaning Up")

        session.query(Device).delete()
        session.query(Order).delete()
        session.query(AuditLog).delete()

        session.commit()

        print("Database cleaned.")

        ###################################################
        # VERIFY DELETE
        ###################################################

        print_header("Final Counts")

        print(
            "Orders:",
            session.query(Order).count()
        )

        print(
            "Devices:",
            session.query(Device).count()
        )

        print(
            "Audit Logs:",
            session.query(AuditLog).count()
        )

    finally:
        session.close()


def test_database_script():
    main()


if __name__ == "__main__":
    main()