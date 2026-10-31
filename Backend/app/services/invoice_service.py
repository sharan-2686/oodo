from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.billing import Invoice, InvoiceItem
from app.models.customer import Customer
from app.schemas.billing import InvoiceCreate

MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def create_invoice(db: Session, payload: InvoiceCreate) -> Invoice:
    customer = db.get(Customer, payload.customer_id)
    if not customer or not customer.is_active:
        raise HTTPException(404, "active customer not found")
    if payload.due_date < date.today():
        raise HTTPException(422, "due_date cannot be in the past")

    invoice = Invoice(
        invoice_number=f"INV-{uuid4().hex[:10].upper()}", customer_id=customer.id,
        issue_date=date.today(), due_date=payload.due_date,
        customer_name_snapshot=customer.name, customer_email_snapshot=customer.email,
    )
    subtotal = tax = Decimal("0")
    for line in payload.items:
        line_subtotal = money(line.quantity * line.unit_price)
        line_tax = money(line_subtotal * line.tax_rate_percent / Decimal("100"))
        invoice.items.append(InvoiceItem(
            description_snapshot=line.description, quantity=line.quantity, unit_price=line.unit_price,
            tax_rate_percent=line.tax_rate_percent, line_subtotal=line_subtotal,
            line_tax=line_tax, line_total=money(line_subtotal + line_tax),
        ))
        subtotal += line_subtotal
        tax += line_tax
    invoice.subtotal, invoice.tax_amount = money(subtotal), money(tax)
    invoice.total_amount = money(invoice.subtotal + invoice.tax_amount)
    db.add(invoice)
    db.flush()
    return invoice
