import hashlib
import hmac

import requests
from flask import current_app


class PaymentError(Exception):
    pass


def enabled():
    return bool(current_app.config["PAYMENT_KEY_ID"] and current_app.config["PAYMENT_KEY_SECRET"])


def create_order(order):
    """Create a Razorpay order. No card or sensitive payment data touches this app."""
    if not enabled():
        return None
    response = requests.post(
        "https://api.razorpay.com/v1/orders",
        auth=(current_app.config["PAYMENT_KEY_ID"], current_app.config["PAYMENT_KEY_SECRET"]),
        json={"amount": int(order.total_amount * 100), "currency": "INR", "receipt": f"store-order-{order.id}"},
        timeout=15,
    )
    if not response.ok:
        raise PaymentError("Payment gateway order could not be created.")
    return response.json()


def verify_signature(razorpay_order_id, razorpay_payment_id, signature):
    secret = current_app.config["PAYMENT_KEY_SECRET"].encode()
    payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")
