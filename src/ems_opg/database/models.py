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

    # part_number removed - orders are created with just a number and a
    # target quantity (see OrderService.create_order); this app no longer
    # tracks which part a job is for.

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

    # Both MAC columns are nullable now: a device that has only ever
    # failed has never been issued MACs at all - they're claimed "a la
    # carte" from the shared pool, and only on a PASS (see
    # DeviceService.record_result). A unique index still permits any
    # number of NULLs, so a device WITH addresses keeps the "one device
    # per MAC" guarantee.
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

    # Repurposed: no longer "has this pre-provisioned slot been claimed".
    # Now means "does this device currently hold a MAC pair", which is
    # true exactly when test_result == "PASS". Kept as a real column
    # (rather than derived from test_result) so it stays cheap to filter
    # and index on directly.
    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    test_result: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
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

    # One Device -> Many failure notes. Every FAIL (first attempt or a
    # later retest of the same serial+order) appends a row here instead
    # of overwriting anything on the device itself, so a board that fails
    # twice keeps both comments visible in its history.
    failure_notes: Mapped[list["DeviceFailureNote"]] = relationship(
        "DeviceFailureNote",
        back_populates="device",
        cascade="all, delete-orphan",
        order_by="DeviceFailureNote.timestamp",
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
# Device Failure Notes
# ---------------------------------------------------------

class DeviceFailureNote(Base):
    """
    One row per failed test attempt. Device rows are reused across
    retests (order+serial is unique), so this table is the only place a
    full failure history survives a later PASS or a second FAIL.
    """

    __tablename__ = "device_failure_notes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id"),
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

    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="failure_notes",
    )

    def __repr__(self):
        return f"<DeviceFailureNote(device_id={self.device_id}, {self.timestamp})>"


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
