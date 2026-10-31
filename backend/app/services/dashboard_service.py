from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from typing import List, Dict

from app.models.subscription import Subscription
from app.models.billing import Invoice, Payment
from app.models.customer import Customer
from app.schemas.dashboard import DashboardSummaryResponse, OverdueInvoiceItem
from app.services.pricing_service import quantize_money

class DashboardService:
    @staticmethod
    def get_summary(db: Session) -> DashboardSummaryResponse:
        today = date.today()

        # 1. Active Subscriptions Count
        active_subs_count = db.query(Subscription).filter(Subscription.status == "active").count()

        # 2. Subscriptions Breakdown
        status_counts_raw = db.query(
            Subscription.status,
            func.count(Subscription.id)
        ).group_by(Subscription.status).all()
        subscriptions_by_status: Dict[str, int] = {status: count for status, count in status_counts_raw}

        # 3. Total Revenue Collected (succeeded payments)
        rev_collected_raw = db.query(func.sum(Payment.amount)).filter(Payment.status == "succeeded").scalar()
        total_revenue_collected = quantize_money(Decimal(str(rev_collected_raw or 0)))

        # 4. Total Invoices Count & Outstanding Revenue
        unpaid_invoices = db.query(Invoice).filter(
            Invoice.status.in_(["confirmed", "issued", "partially_paid", "overdue", "draft"])
        ).all()

        total_invoices_count = db.query(Invoice).count()

        total_revenue_owed = Decimal("0.00")
        overdue_items: List[OverdueInvoiceItem] = []

        for inv in unpaid_invoices:
            bal = inv.balance_due
            if bal > Decimal("0.00"):
                total_revenue_owed += bal

            # Check overdue
            if inv.due_date < today and bal > Decimal("0.00") and inv.status != "void":
                # Automatically mark overdue if not already
                if inv.status != "overdue":
                    inv.status = "overdue"
                days_overdue = (today - inv.due_date).days
                overdue_items.append(
                    OverdueInvoiceItem(
                        id=inv.id,
                        invoice_number=inv.invoice_number,
                        customer_id=inv.customer_id,
                        customer_name=inv.customer_name_snapshot,
                        issue_date=inv.issue_date,
                        due_date=inv.due_date,
                        total_amount=quantize_money(inv.total_amount),
                        amount_paid=quantize_money(inv.amount_paid),
                        balance_due=quantize_money(bal),
                        days_overdue=days_overdue
                    )
                )

        # Commit any auto-marked overdue statuses
        db.commit()

        # Sort overdue invoices descending by days overdue
        overdue_items.sort(key=lambda x: x.days_overdue, reverse=True)

        return DashboardSummaryResponse(
            active_subscriptions_count=active_subs_count,
            total_revenue_collected=total_revenue_collected,
            total_revenue_owed=quantize_money(total_revenue_owed),
            total_invoices_count=total_invoices_count,
            overdue_invoices_count=len(overdue_items),
            overdue_invoices=overdue_items,
            subscriptions_by_status=subscriptions_by_status
        )
