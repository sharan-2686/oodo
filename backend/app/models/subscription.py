from datetime import date, datetime
from decimal import Decimal
import enum
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    JSON,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import (
    Base,
    BigIntFK,
    BigIntPK,
    MoneyAmount,
    QuantityAmount,
    UTCDateTime,
    get_utc_now,
)
from app.models.catalog import BillingInterval


class SubscriptionStatus(str, enum.Enum):
    DRAFT = "draft"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(Base):
    __tablename__ = "subscriptions"

    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="chk_sub_unit_price"),
        CheckConstraint("quantity > 0", name="chk_sub_quantity"),
        CheckConstraint("interval_count >= 1", name="chk_sub_interval_count"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    subscription_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    plan_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quotation_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("quotations.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )
    discount_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("discounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=SubscriptionStatus.DRAFT,
        nullable=False,
        index=True,
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        QuantityAmount, default=Decimal("1.000"), nullable=False
    )
    billing_interval: Mapped[BillingInterval] = mapped_column(
        Enum(BillingInterval, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    interval_count: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    trial_ends_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    next_billing_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True, index=True
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_by: Mapped[int | None] = mapped_column(
        BigIntFK, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    quotation = relationship("Quotation", back_populates="subscription")
    discount = relationship("Discount")
    created_by_user = relationship("User", foreign_keys=[created_by])
    items: Mapped[List["SubscriptionItem"]] = relationship(
        "SubscriptionItem", back_populates="subscription", cascade="all, delete-orphan"
    )
    events: Mapped[List["SubscriptionEvent"]] = relationship(
        "SubscriptionEvent", back_populates="subscription", cascade="all, delete-orphan"
    )
    invoices = relationship("Invoice", back_populates="subscription")
    billing_runs = relationship("BillingRun", back_populates="subscription")


class SubscriptionItem(Base):
    __tablename__ = "subscription_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_sub_item_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_sub_item_unit_price"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    variant_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("product_variants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        QuantityAmount, default=Decimal("1.000"), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class SubscriptionEvent(Base):
    __tablename__ = "subscription_events"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    actor_user_id: Mapped[int | None] = mapped_column(
        BigIntFK, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="events")
    actor_user = relationship("User", foreign_keys=[actor_user_id])
