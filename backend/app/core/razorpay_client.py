"""
Razorpay SDK singleton and HMAC signature verification utilities.

IMPORTANT SEPARATION:
  - Checkout (frontend redirect) signature  → verified with RAZORPAY_KEY_SECRET
  - Webhook (server-to-server) signature    → verified with RAZORPAY_WEBHOOK_SECRET
These two secrets and verification paths must NEVER be mixed.
"""

import hashlib
import hmac
import logging
from functools import lru_cache
from typing import Optional

import razorpay

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_razorpay_client() -> razorpay.Client:
    """Return a singleton Razorpay client initialized from environment variables."""
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise RuntimeError(
            "Razorpay credentials are not configured. "
            "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your .env file."
        )
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    client.set_app_details({"title": "Brightloop360", "version": "1.0.0"})
    logger.info("Razorpay client initialized (key_id=%s)", settings.RAZORPAY_KEY_ID)
    return client


def verify_checkout_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> bool:
    """
    Verify the signature returned by Razorpay to the frontend after payment.

    Uses RAZORPAY_KEY_SECRET (API Key Secret) — NOT the webhook secret.
    HMAC-SHA256 of "{order_id}|{payment_id}" must equal razorpay_signature.
    """
    if not settings.RAZORPAY_KEY_SECRET:
        logger.error("RAZORPAY_KEY_SECRET is not set — cannot verify checkout signature")
        return False

    message = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, razorpay_signature)


def verify_webhook_signature(
    raw_body: bytes,
    signature_header: Optional[str],
) -> bool:
    """
    Verify the X-Razorpay-Signature header on incoming webhook requests.

    Uses RAZORPAY_WEBHOOK_SECRET — NOT the API Key Secret.
    HMAC-SHA256 of the raw request body must equal the header value.
    """
    if not signature_header:
        logger.warning("Webhook request missing X-Razorpay-Signature header")
        return False

    if not settings.RAZORPAY_WEBHOOK_SECRET:
        logger.error("RAZORPAY_WEBHOOK_SECRET is not set — rejecting all webhook requests")
        return False

    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
