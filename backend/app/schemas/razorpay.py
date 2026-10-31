"""
Pydantic schemas for Razorpay order creation and payment verification APIs.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class RazorpayOrderCreateRequest(BaseModel):
    """Request body for creating a Razorpay order for a specific invoice."""
    invoice_id: int = Field(..., description="Internal invoice ID to pay")


class RazorpayOrderCreateResponse(BaseModel):
    """Response returned to the frontend to initialize the Razorpay Checkout widget."""
    razorpay_order_id: str = Field(..., description="Razorpay Order ID (order_xxx)")
    amount_paise: int = Field(..., description="Amount in paise (INR × 100)")
    currency: str = Field("INR")
    key_id: str = Field(..., description="Razorpay Public Key ID — safe to expose to frontend")
    internal_payment_id: int = Field(..., description="Internal Payment record ID")
    invoice_id: int
    invoice_number: str
    balance_due: Decimal = Field(..., description="Outstanding balance in INR")


class RazorpayVerifyRequest(BaseModel):
    """
    Request body for server-side payment verification after Razorpay checkout success.
    These three fields are returned by the Razorpay checkout widget.
    """
    razorpay_order_id: str = Field(..., description="Razorpay Order ID returned by checkout")
    razorpay_payment_id: str = Field(..., description="Razorpay Payment ID returned by checkout")
    razorpay_signature: str = Field(..., description="HMAC-SHA256 signature returned by checkout")
    invoice_id: int = Field(..., description="Internal invoice ID being paid")


class RazorpayVerifyResponse(BaseModel):
    """Response returned after successful payment verification and capture."""
    success: bool
    message: str
    payment_id: Optional[int] = None
    payment_number: Optional[str] = None
    invoice_id: Optional[int] = None
    invoice_status: Optional[str] = None
    amount_paid: Optional[Decimal] = None
    balance_due: Optional[Decimal] = None
