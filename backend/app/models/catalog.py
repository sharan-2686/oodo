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
    Integer,
    JSON,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import (
    Base,
    BigIntFK,
    BigIntPK,
    MoneyAmount,
    QuantityAmount,
    TaxRatePercent,
    UTCDateTime,
    get_utc_now,
)


class BillingInterval(str, enum.Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    variants: Mapped[List["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="chk_variant_unit_price"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")


class Plan(Base):
    __tablename__ = "plans"

    __table_args__ = (
        CheckConstraint("interval_count >= 1", name="chk_plan_interval_count"),
        CheckConstraint("base_price >= 0", name="chk_plan_base_price"),
        CheckConstraint("trial_days >= 0", name="chk_plan_trial_days"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    billing_interval: Mapped[BillingInterval] = mapped_column(
        Enum(BillingInterval, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    interval_count: Mapped[int] = mapped_column(
        SmallInteger, default=1, nullable=False
    )
    base_price: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    trial_days: Mapped[int] = mapped_column(
        SmallInteger, default=0, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    items: Mapped[List["PlanItem"]] = relationship(
        "PlanItem", back_populates="plan", cascade="all, delete-orphan"
    )
    subscriptions = relationship("Subscription", back_populates="plan")


class PlanItem(Base):
    __tablename__ = "plan_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_plan_item_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_plan_item_unit_price"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("plans.id", ondelete="CASCADE"),
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
    plan: Mapped["Plan"] = relationship("Plan", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant")


class Discount(Base):
    __tablename__ = "discounts"

    __table_args__ = (
        CheckConstraint("discount_value > 0", name="chk_discount_value"),
        CheckConstraint("redemption_count >= 0", name="chk_discount_redemption_count"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    discount_type: Mapped[DiscountType] = mapped_column(
        Enum(DiscountType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    discount_value: Mapped[Decimal] = mapped_column(MoneyAmount, nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    redemption_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )


class TaxRate(Base):
    __tablename__ = "tax_rates"

    __table_args__ = (
        CheckConstraint(
            "rate_percent >= 0 AND rate_percent <= 100",
            name="chk_tax_rate_percent",
        ),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    rate_percent: Mapped[Decimal] = mapped_column(TaxRatePercent, nullable=False)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_inclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )
