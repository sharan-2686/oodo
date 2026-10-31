from datetime import date, datetime
from decimal import Decimal
import enum
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    JSON,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
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


class InvoiceType(str, enum.Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    ADJUSTMENT = "adjustment"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    UPI = "upi"
    GATEWAY = "gateway"
    OTHER = "other"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class BillingRunStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Invoice(Base):
    __tablename__ = "invoices"

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="chk_invoice_subtotal"),
        CheckConstraint("discount_amount >= 0", name="chk_invoice_discount_amount"),
        CheckConstraint("tax_amount >= 0", name="chk_invoice_tax_amount"),
        CheckConstraint("total_amount >= 0", name="chk_invoice_total_amount"),
        CheckConstraint("due_date >= issue_date", name="chk_invoice_due_date"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    subscription_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    discount_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("discounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    invoice_type: Mapped[InvoiceType] = mapped_column(
        Enum(InvoiceType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=InvoiceStatus.DRAFT,
        nullable=False,
        index=True,
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    billing_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    billing_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)

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

    discount_code_snapshot: Mapped[str | None] = mapped_column(String(60), nullable=True)
    customer_name_snapshot: Mapped[str] = mapped_column(String(180), nullable=False)
    customer_email_snapshot: Mapped[str | None] = mapped_column(String(254), nullable=True)
    billing_address_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    customer = relationship("Customer", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    discount = relationship("Discount")
    created_by_user = relationship("User", foreign_keys=[created_by])
    items: Mapped[List["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    payment_allocations: Mapped[List["PaymentAllocation"]] = relationship(
        "PaymentAllocation", back_populates="invoice"
    )
    billing_run = relationship("BillingRun", back_populates="invoice", uselist=False)

    @property
    def amount_paid(self) -> Decimal:
        allocs = self.payment_allocations
        if not allocs:
            return Decimal("0.00")
        return sum((a.amount_allocated for a in allocs), Decimal("0.00"))

    @property
    def balance_due(self) -> Decimal:
        total = self.total_amount if self.total_amount is not None else Decimal("0.00")
        return max(Decimal("0.00"), total - self.amount_paid)

    @property
    def allocations(self):
        return self.payment_allocations



class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_invoice_item_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_invoice_item_unit_price"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("invoices.id", ondelete="CASCADE"),
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
    description_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    sku_snapshot: Mapped[str | None] = mapped_column(String(80), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(
        QuantityAmount, default=Decimal("1.000"), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        MoneyAmount, default=Decimal("0.00"), nullable=False
    )
    tax_rate_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("tax_rates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    tax_name_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
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
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    plan = relationship("Plan")
    tax_rate = relationship("TaxRate")


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payment_amount"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    payment_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(MoneyAmount, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )
    transaction_reference: Mapped[str | None] = mapped_column(String(150), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(
        BigIntFK, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )

    # Relationships
    customer = relationship("Customer", back_populates="payments")
    created_by_user = relationship("User", foreign_keys=[created_by])
    allocations: Mapped[List["PaymentAllocation"]] = relationship(
        "PaymentAllocation", back_populates="payment", cascade="all, delete-orphan"
    )

    @property
    def total_allocated(self) -> Decimal:
        if not self.allocations:
            return Decimal("0.00")
        return sum((a.amount_allocated for a in self.allocations), Decimal("0.00"))

    @property
    def unallocated_amount(self) -> Decimal:
        amt = self.amount if self.amount is not None else Decimal("0.00")
        return max(Decimal("0.00"), amt - self.total_allocated)



class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    __table_args__ = (
        CheckConstraint("amount_allocated > 0", name="chk_alloc_amount"),
        UniqueConstraint("payment_id", "invoice_id", name="uq_payment_invoice_alloc"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount_allocated: Mapped[Decimal] = mapped_column(MoneyAmount, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )

    # Relationships
    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payment_allocations")


class BillingRun(Base):
    __tablename__ = "billing_runs"

    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "billing_period_start",
            "billing_period_end",
            name="uq_sub_billing_period",
        ),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(
        BigIntFK,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[int | None] = mapped_column(
        BigIntFK,
        ForeignKey("invoices.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )
    billing_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    billing_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[BillingRunStatus] = mapped_column(
        Enum(BillingRunStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=BillingRunStatus.PENDING,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(
        SmallInteger, default=0, nullable=False
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False
    )

    # Relationships
    subscription = relationship("Subscription", back_populates="billing_runs")
    invoice = relationship("Invoice", back_populates="billing_run")
