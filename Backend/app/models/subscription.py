from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.mixins import TimestampMixin


class Subscription(TimestampMixin, Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=1)
    billing_interval: Mapped[str] = mapped_column(String(10))
    interval_count: Mapped[int] = mapped_column(default=1)
    start_date: Mapped[date] = mapped_column(Date)
    next_billing_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    customer: Mapped["Customer"] = relationship(back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")
    items: Mapped[list["SubscriptionItem"]] = relationship(back_populates="subscription", cascade="all, delete-orphan")


class SubscriptionItem(Base):
    __tablename__ = "subscription_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"))
    description_snapshot: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subscription: Mapped[Subscription] = relationship(back_populates="items")


class BillingRun(Base):
    __tablename__ = "billing_runs"
    __table_args__ = (UniqueConstraint("subscription_id", "billing_period_start", "billing_period_end", name="subscription_period"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"), unique=True)
    billing_period_start: Mapped[date] = mapped_column(Date)
    billing_period_end: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")
