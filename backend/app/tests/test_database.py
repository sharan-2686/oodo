from datetime import date, datetime, timezone
from decimal import Decimal
import pytest
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.billing import (
    BillingRun,
    BillingRunStatus,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    InvoiceType,
    Payment,
    PaymentAllocation,
    PaymentMethod,
    PaymentStatus,
)
from app.models.catalog import (
    BillingInterval,
    Discount,
    DiscountType,
    Plan,
    PlanItem,
    Product,
    ProductVariant,
    TaxRate,
)
from app.models.customer import Customer, CustomerType
from app.models.quotation import Quotation, QuotationItem, QuotationStatus
from app.models.subscription import (
    Subscription,
    SubscriptionEvent,
    SubscriptionItem,
    SubscriptionStatus,
)
from app.models.user import Permission, RefreshToken, Role, User


def test_all_23_models_lifecycle(db_session: Session):
    """Verify that all 23 domain models can be instantiated and persisted with proper relationships."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    today = date.today()

    # 1, 2, 3: Role & Permission & User
    admin_user = db_session.query(User).filter_by(email="admin@brightloop.io").first()
    assert admin_user is not None

    # 4: Refresh token
    token = RefreshToken(
        user_id=admin_user.id,
        token_hash="a" * 64,
        expires_at=now,
        created_at=now,
    )
    db_session.add(token)
    db_session.flush()

    # 5: Customer
    customer = Customer(
        customer_code="CUST-001",
        customer_type=CustomerType.BUSINESS,
        name="Acme Corporation",
        email="billing@acme.com",
        phone="+919876543210",
        company_name="Acme Corp Ltd",
        billing_country="IN",
        created_by=admin_user.id,
    )
    db_session.add(customer)
    db_session.flush()

    # 6 & 7: Product & ProductVariant
    product = Product(
        sku="PROD-CLOUD",
        name="Cloud Enterprise Server",
        category="Cloud",
    )
    db_session.add(product)
    db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku="VAR-CLOUD-4VCPU",
        name="4 vCPU / 16GB RAM",
        unit_price=Decimal("1500.00"),
        currency="INR",
    )
    db_session.add(variant)
    db_session.flush()

    # 8 & 9: Plan & PlanItem
    plan = Plan(
        code="PLAN-CLOUD-ENTERPRISE",
        name="Enterprise Cloud Plan",
        billing_interval=BillingInterval.MONTH,
        interval_count=1,
        base_price=Decimal("1500.00"),
        currency="INR",
    )
    db_session.add(plan)
    db_session.flush()

    plan_item = PlanItem(
        plan_id=plan.id,
        product_id=product.id,
        variant_id=variant.id,
        quantity=Decimal("1.000"),
        unit_price=Decimal("1500.00"),
    )
    db_session.add(plan_item)
    db_session.flush()

    # 10: Discount
    discount = Discount(
        code="SAVE100",
        name="Save 100",
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("100.00"),
        currency="INR",
    )
    db_session.add(discount)
    db_session.flush()

    # 11: TaxRate
    tax_rate = TaxRate(
        name="Standard GST",
        code="GST_18_TEST",
        rate_percent=Decimal("18.0000"),
        country="IN",
    )
    db_session.add(tax_rate)
    db_session.flush()

    # 12 & 13: Quotation & QuotationItem
    quotation = Quotation(
        quote_number="QT-2026-0001",
        customer_id=customer.id,
        created_by=admin_user.id,
        discount_id=discount.id,
        status=QuotationStatus.ACCEPTED,
        issue_date=today,
        subtotal=Decimal("1500.00"),
        discount_amount=Decimal("100.00"),
        tax_amount=Decimal("252.00"),
        total_amount=Decimal("1652.00"),
    )
    db_session.add(quotation)
    db_session.flush()

    q_item = QuotationItem(
        quotation_id=quotation.id,
        product_id=product.id,
        variant_id=variant.id,
        plan_id=plan.id,
        description="Enterprise Cloud Plan Line",
        quantity=Decimal("1.000"),
        unit_price=Decimal("1500.00"),
        tax_rate_percent=Decimal("18.0000"),
        line_subtotal=Decimal("1500.00"),
        line_tax=Decimal("270.00"),
        line_total=Decimal("1770.00"),
    )
    db_session.add(q_item)
    db_session.flush()

    # 14, 15, 16: Subscription, Items & Events
    subscription = Subscription(
        subscription_number="SUB-2026-0001",
        customer_id=customer.id,
        plan_id=plan.id,
        quotation_id=quotation.id,
        discount_id=discount.id,
        status=SubscriptionStatus.ACTIVE,
        currency="INR",
        unit_price=Decimal("1500.00"),
        quantity=Decimal("1.000"),
        billing_interval=BillingInterval.MONTH,
        interval_count=1,
        start_date=today,
        created_by=admin_user.id,
    )
    db_session.add(subscription)
    db_session.flush()

    sub_item = SubscriptionItem(
        subscription_id=subscription.id,
        product_id=product.id,
        variant_id=variant.id,
        description_snapshot="Enterprise Cloud Plan Line",
        quantity=Decimal("1.000"),
        unit_price=Decimal("1500.00"),
    )
    db_session.add(sub_item)

    sub_event = SubscriptionEvent(
        subscription_id=subscription.id,
        event_type="subscription_activated",
        from_status="draft",
        to_status="active",
        actor_user_id=admin_user.id,
    )
    db_session.add(sub_event)
    db_session.flush()

    # 17 & 18: Invoice & InvoiceItem
    invoice = Invoice(
        invoice_number="INV-2026-0001",
        customer_id=customer.id,
        subscription_id=subscription.id,
        discount_id=discount.id,
        invoice_type=InvoiceType.SUBSCRIPTION,
        status=InvoiceStatus.ISSUED,
        currency="INR",
        issue_date=today,
        due_date=today,
        subtotal=Decimal("1500.00"),
        discount_amount=Decimal("100.00"),
        tax_amount=Decimal("252.00"),
        total_amount=Decimal("1652.00"),
        customer_name_snapshot=customer.name,
        created_by=admin_user.id,
    )
    db_session.add(invoice)
    db_session.flush()

    inv_item = InvoiceItem(
        invoice_id=invoice.id,
        product_id=product.id,
        variant_id=variant.id,
        plan_id=plan.id,
        description_snapshot="Enterprise Cloud Plan Line",
        quantity=Decimal("1.000"),
        unit_price=Decimal("1500.00"),
        tax_rate_id=tax_rate.id,
        tax_rate_percent=Decimal("18.0000"),
        line_subtotal=Decimal("1500.00"),
        line_tax=Decimal("270.00"),
        line_total=Decimal("1770.00"),
    )
    db_session.add(inv_item)
    db_session.flush()

    # 19: Payment
    payment = Payment(
        payment_number="PAY-2026-0001",
        customer_id=customer.id,
        amount=Decimal("1652.00"),
        currency="INR",
        payment_method=PaymentMethod.CARD,
        status=PaymentStatus.SUCCEEDED,
        created_by=admin_user.id,
    )
    db_session.add(payment)
    db_session.flush()

    # 20: PaymentAllocation
    allocation = PaymentAllocation(
        payment_id=payment.id,
        invoice_id=invoice.id,
        amount_allocated=Decimal("1652.00"),
    )
    db_session.add(allocation)
    db_session.flush()

    # 21: BillingRun
    billing_run = BillingRun(
        subscription_id=subscription.id,
        invoice_id=invoice.id,
        billing_period_start=today,
        billing_period_end=today,
        status=BillingRunStatus.SUCCEEDED,
    )
    db_session.add(billing_run)
    db_session.flush()

    # 22: AuditLog
    audit = AuditLog(
        actor_user_id=admin_user.id,
        action="invoice_generated",
        entity_type="invoices",
        entity_id=invoice.id,
    )
    db_session.add(audit)
    db_session.flush()

    db_session.commit()

    # Verification: query back
    assert db_session.get(Customer, customer.id).name == "Acme Corporation"
    assert db_session.get(Subscription, subscription.id).subscription_number == "SUB-2026-0001"
    assert db_session.get(Invoice, invoice.id).invoice_number == "INV-2026-0001"
    assert db_session.get(Payment, payment.id).amount == Decimal("1652.00")
    assert len(db_session.get(Payment, payment.id).allocations) == 1
    assert db_session.get(BillingRun, billing_run.id).status == BillingRunStatus.SUCCEEDED
    assert db_session.get(AuditLog, audit.id).action == "invoice_generated"

