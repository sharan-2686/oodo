from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from app.models.catalog import Discount, TaxRate

def quantize_money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def quantize_qty(qty: Decimal) -> Decimal:
    return qty.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

class PricingService:
    @staticmethod
    def calculate_line_item(
        quantity: Decimal,
        unit_price: Decimal,
        tax_rate_percent: Decimal = Decimal("0.0000"),
        is_inclusive: bool = False
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Returns (line_subtotal, line_tax, line_total)
        """
        raw_subtotal = Decimal(str(quantity)) * Decimal(str(unit_price))
        rate = Decimal(str(tax_rate_percent)) / Decimal("100.0000")
        
        if is_inclusive and rate > 0:
            base = raw_subtotal / (Decimal("1.0000") + rate)
            line_tax = quantize_money(raw_subtotal - base)
            line_subtotal = quantize_money(base)
            line_total = quantize_money(raw_subtotal)
        else:
            line_subtotal = quantize_money(raw_subtotal)
            line_tax = quantize_money(line_subtotal * rate)
            line_total = line_subtotal + line_tax
            
        return line_subtotal, line_tax, line_total

    @staticmethod
    def evaluate_discount(
        discount: Optional[Discount],
        subtotal: Decimal,
        total_quantity: Decimal = Decimal("1.000")
    ) -> Decimal:
        """
        Calculates eligible discount amount based on rules:
        - Active status
        - Validity window
        - Max redemptions
        - Minimum purchase amount or quantity (if present)
        """
        if not discount or not discount.is_active:
            return Decimal("0.00")
            
        now = datetime.now(timezone.utc)
        if discount.starts_at and discount.starts_at.tzinfo is None:
            starts_at = discount.starts_at.replace(tzinfo=timezone.utc)
        else:
            starts_at = discount.starts_at
            
        if discount.ends_at and discount.ends_at.tzinfo is None:
            ends_at = discount.ends_at.replace(tzinfo=timezone.utc)
        else:
            ends_at = discount.ends_at

        if starts_at and now < starts_at:
            return Decimal("0.00")
        if ends_at and now > ends_at:
            return Decimal("0.00")
            
        if discount.max_redemptions is not None and discount.redemption_count >= discount.max_redemptions:
            return Decimal("0.00")
            
        min_purchase = getattr(discount, "min_purchase_amount", None)
        if min_purchase and subtotal < Decimal(str(min_purchase)):
            return Decimal("0.00")
            
        min_qty = getattr(discount, "min_quantity", None)
        if min_qty and total_quantity < Decimal(str(min_qty)):
            return Decimal("0.00")

        if discount.discount_type == "percentage":
            percent = Decimal(str(discount.discount_value)) / Decimal("100.00")
            discount_amount = quantize_money(subtotal * percent)
        else:
            discount_amount = quantize_money(Decimal(str(discount.discount_value)))
            
        return min(discount_amount, subtotal)
