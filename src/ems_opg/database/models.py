from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# ---------------------------------------------------------
# Orders
# ---------------------------------------------------------

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Open",
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    # Failures are order-scoped, not device-scoped - a failed board never
    # gets a serial/MAC, so there's no Device row to attach a failure to.
    # See OrderFailure below.
    failures: Mapped[list["OrderFailure"]] = relationship(
        "OrderFailure",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderFailure.timestamp",
    )

    def __repr__(self):
        return (
            f"<Order("
            f"order_number={self.order_number}, "
            f"quantity={self.quantity}, "
            f"status={self.status})>"
        )


# ---------------------------------------------------------
# Devices
# ---------------------------------------------------------

class Device(Base):
    """
    A Device row only ever exists for a board that has already passed -
    serial numbers are assigned at the end of a passing test, so there is
    no "failed device" row anymore (see OrderFailure). Every row here is
    implicitly a PASS.
    """

    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint(
            "order_number",
            "serial_number",
            name="uq_device_order_serial"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    order_number: Mapped[str] = mapped_column(
        ForeignKey("orders.order_number"),
        nullable=False,
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    ethaddr_id: Mapped[str | None] = mapped_column(
        String(17),
        unique=True,
        nullable=True,
        index=True,
    )

    eth1addr_id: Mapped[str | None] = mapped_column(
        String(17),
        unique=True,
        nullable=True,
        index=True,
    )

    # Always True in practice now - kept for the CSV export's
    # "Used/Available" column and to avoid touching every call site that
    # reads it.
    used: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    test_result: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="PASS",
    )

    operator: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    post_test_changes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="devices"
    )

    def __repr__(self):
        return (
            f"<Device("
            f"serial={self.serial_number}, "
            f"first_mac={self.ethaddr_id},"
            f"second_mac={self.eth1addr_id})>"
        )

#---------------------------------------------------------
# MAC Address Pool
#---------------------------------------------------------

class MACAddressPool(Base):
    __tablename__ = "mac_address_pool"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    mac_address: Mapped[str] = mapped_column(
        String(17),
        unique=True,
        nullable=False,
        index=True,
    )

    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<MACAddressPool("
            f"mac_address={self.mac_address}, "
            f"used={self.used})>"
        )


# ---------------------------------------------------------
# Order Failures
# ---------------------------------------------------------

class OrderFailure(Base):
    """
    One row per failed test attempt under an order. Not linked to any
    specific serial/device - a failed board is set aside and re-enters
    the line as an ordinary board later, with no persisted link back to
    this failure. Exported as a failure-history CSV when the order
    completes (see maybe_export_completed_order in routes.py).
    """

    __tablename__ = "order_failures"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    order_number: Mapped[str] = mapped_column(
        ForeignKey("orders.order_number"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="failures",
    )

    def __repr__(self):
        return f"<OrderFailure(order_number={self.order_number}, {self.timestamp})>"


# ---------------------------------------------------------
# Audit Log
# ---------------------------------------------------------

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    def __repr__(self):
        return f"<AuditLog({self.timestamp} {self.action})>"