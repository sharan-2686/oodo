from datetime import date, datetime
from decimal import Decimal
import enum
from typing import List, Optional
from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
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


class QuotationStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"


class Quotation(Base):
    __tablename__ = "quotations"

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="chk_quote_subtotal"),
        CheckConstraint("discount_amount >= 0", name="chk_quote_discount_amount"),
        CheckConstraint("tax_amount >= 0", name="chk_quote_tax_amount"),
        CheckConstraint("total_amount >= 0", name="chk_quote_total_amount"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    quote_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[int | None] = mapped_column(
        BigIntFK, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    discount_id: Mapped[int | None] = mapped_column(
        BigIntFK, ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[QuotationStatus] = mapped_column(
        Enum(QuotationStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=QuotationStatus.DRAFT,
        nullable=False,
    )
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    subtotal: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )

    terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    customer = relationship("Customer", back_populates="quotations")
    created_by_user = relationship("User", foreign_keys=[created_by])
    discount = relationship("Discount")
    items: Mapped[List["QuotationItem"]] = relationship(
        "QuotationItem", back_populates="quotation", cascade="all, delete-orphan"
    )
    subscription = relationship(
        "Subscription", back_populates="quotation", uselist=False
    )


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_quote_item_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_quote_item_unit_price"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    quotation_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    variant_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("product_variants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    plan_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        QuantityAmount, default=Decimal("1.000"), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    tax_rate_percent: Mapped[Decimal] = mapped_column(
        TaxRatePercent, default=Decimal("0.0000"), nullable=False
    )
    line_subtotal: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    line_tax: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    line_total: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )

    # Relationships
    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    plan = relationship("Plan")
