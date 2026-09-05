from decimal import Decimal

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from .. import db
from ..models import Customer, Order, OrderItem, Product
from ..services.email_service import send_order_confirmation
from ..services.payment_service import PaymentError, create_order, enabled, verify_signature
from .cart import cart_details

bp = Blueprint("checkout", __name__, url_prefix="/checkout")


def shipping_for(subtotal):
    if subtotal >= current_app.config["FREE_SHIPPING_THRESHOLD"]:
        return Decimal("0.00")
    return Decimal(current_app.config["SHIPPING_FLAT_RATE"])


@bp.route("/", methods=["GET", "POST"])
def checkout():
    rows, subtotal = cart_details()
    if not rows:
        flash("Your cart is empty.", "error")
        return redirect(url_for("products.listing"))
    shipping = shipping_for(subtotal)
    if request.method == "POST":
        fields = {name: request.form.get(name, "").strip() for name in ("name", "email", "phone", "address_line1", "address_line2", "city", "state", "pincode")}
        required = ("name", "email", "phone", "address_line1", "city", "state", "pincode")
        if any(not fields[name] for name in required) or "@" not in fields["email"]:
            flash("Please provide a valid name, email and complete delivery address.", "error")
            return render_template("checkout.html", rows=rows, subtotal=subtotal, shipping=shipping, total=subtotal + shipping, form=fields)
        # Recheck stock/prices from the database immediately before order creation.
        for row in rows:
            if row["quantity"] > row["product"].stock_quantity:
                flash(f"{row['product'].name} no longer has enough stock.", "error")
                return redirect(url_for("cart.view"))
        customer = Customer(name=fields["name"], email=fields["email"], phone=fields["phone"])
        address = ", ".join(value for value in [fields["name"], fields["phone"], fields["address_line1"], fields["address_line2"], fields["city"], fields["state"], fields["pincode"], "India"] if value)
        order = Order(customer=customer, total_amount=subtotal + shipping, shipping_address=address)
        for row in rows:
            product = row["product"]
            order.items.append(OrderItem(product_id=product.id, product_name=product.name, quantity=row["quantity"], price=product.price, subtotal=row["line_total"]))
        db.session.add(order)
        db.session.commit()
        if enabled():
            try:
                gateway_order = create_order(order)
                order.payment_reference = gateway_order["id"]
                db.session.commit()
                return render_template("payment.html", order=order, gateway_order=gateway_order, key_id=current_app.config["PAYMENT_KEY_ID"])
            except PaymentError as exc:
                db.session.rollback()
                flash(str(exc), "error")
                return redirect(url_for("checkout.checkout"))
        # Development safety: no payment is marked paid without a verified gateway callback.
        session["cart"] = {}
        session.modified = True
        return redirect(url_for("checkout.success", order_id=order.id))
    return render_template("checkout.html", rows=rows, subtotal=subtotal, shipping=shipping, total=subtotal + shipping, form={})


@bp.post("/payment/verify")
def payment_verify():
    order = db.session.get(Order, request.form.get("local_order_id", type=int))
    if not order or order.payment_status == "paid":
        return {"ok": False, "message": "Invalid or already processed order."}, 400
    if not verify_signature(request.form.get("razorpay_order_id"), request.form.get("razorpay_payment_id"), request.form.get("razorpay_signature")):
        return {"ok": False, "message": "Payment signature verification failed."}, 400
    order.payment_status, order.order_status = "paid", "confirmed"
    order.payment_reference = request.form.get("razorpay_payment_id")
    for item in order.items:
        product = db.session.get(Product, item.product_id)
        if product and product.stock_quantity >= item.quantity:
            product.stock_quantity -= item.quantity
    db.session.commit()
    try:
        send_order_confirmation(order)
    except Exception:
        current_app.logger.exception("Order email failed for %s", order.id)
    session["cart"] = {}
    return {"ok": True, "redirect": url_for("checkout.success", order_id=order.id)}


@bp.get("/success/<int:order_id>")
def success(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return redirect(url_for("main.home"))
    return render_template("order_success.html", order=order)
