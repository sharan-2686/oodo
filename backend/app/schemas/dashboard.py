from pydantic import BaseModel
from typing import List, Dict
from decimal import Decimal
from datetime import date

class OverdueInvoiceItem(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    customer_name: str
    issue_date: date
    due_date: date
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    days_overdue: int

class DashboardSummaryResponse(BaseModel):
    active_subscriptions_count: int
    total_revenue_collected: Decimal
    total_revenue_owed: Decimal
    total_invoices_count: int
    overdue_invoices_count: int
    overdue_invoices: List[OverdueInvoiceItem]
    subscriptions_by_status: Dict[str, int]
