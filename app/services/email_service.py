import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)


def send_order_confirmation(order):
    subject = f"Your {current_app.config['STORE_NAME']} order #{order.id}"
    body = f"Hi {order.customer.name},\n\nThank you for your order. Total: ₹{order.total_amount}.\nPayment: {order.payment_status}.\n"
    if not current_app.config["MAIL_SERVER"]:
        logger.info("Email not configured. Would send to %s:\n%s", order.customer.email, body)
        return False
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = order.customer.email
    message.set_content(body)
    with smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"], timeout=15) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        if current_app.config["MAIL_USERNAME"]:
            smtp.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
        smtp.send_message(message)
    return True
