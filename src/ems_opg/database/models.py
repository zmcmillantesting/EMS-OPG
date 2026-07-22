from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
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

    part_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Open",
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # One Order -> Many Devices
    devices: Mapped[list["Device"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Order("
            f"order_number={self.order_number}, "
            f"status={self.status})>"
        )


# ---------------------------------------------------------
# Devices
# ---------------------------------------------------------

class Device(Base):
    __tablename__ = "devices"

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
        unique=True,
        nullable=False,
        index=True,
    )

    ethaddr_id: Mapped[str] = mapped_column(
        String(17),
        unique=True,
        nullable=False,
        index=True,
    )

    ethaddr1_id: Mapped[str] = mapped_column(
        String(17),
        unique =True,
        nullable=True,
        index=True,
    )

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

    # Many Devices -> One Order
    order: Mapped["Order"] = relationship(
        back_populates="devices"
    )

    def __repr__(self):
        return (
            f"<Device("
            f"serial={self.serial_number}, "
            f"first_mac={self.first_mac_address})>"
            f"second_mac={self.second_mac_address}>"
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
        return (
            f"<AuditLog("
            f"{self.timestamp} "
            f"{self.action})>"
        )