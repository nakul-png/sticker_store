from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from .. import db
from ..models import Product

bp = Blueprint("cart", __name__, url_prefix="/cart")


def _cart():
    return session.setdefault("cart", {})


def cart_count():
    return sum(int(qty) for qty in session.get("cart", {}).values())


def cart_details():
    cart = _cart()
    ids = [int(id_) for id_ in cart if id_.isdigit()]
    products = db.session.scalars(select(Product).where(Product.id.in_(ids), Product.is_active.is_(True))).all() if ids else []
    rows, subtotal = [], Decimal("0.00")
    for product in products:
        qty = min(max(int(cart.get(str(product.id), 0)), 0), product.stock_quantity)
        if not qty:
            continue
        line_total = product.price * qty
        rows.append({"product": product, "quantity": qty, "line_total": line_total})
        subtotal += line_total
    return rows, subtotal


@bp.get("/")
def view():
    rows, subtotal = cart_details()
    return render_template("cart.html", rows=rows, subtotal=subtotal)


@bp.post("/add/<int:product_id>")
def add(product_id):
    product = db.session.get(Product, product_id)
    if not product or not product.is_active or product.stock_quantity < 1:
        flash("This product is currently unavailable.", "error")
        return redirect(url_for("products.listing"))
    quantity = request.form.get("quantity", 1, type=int)
    cart = _cart()
    new_quantity = min(cart.get(str(product_id), 0) + max(quantity, 1), product.stock_quantity)
    cart[str(product_id)] = new_quantity
    session.modified = True
    flash(f"{product.name} added to your cart.", "success")
    return redirect(request.referrer or url_for("cart.view"))


@bp.post("/update/<int:product_id>")
def update(product_id):
    product = db.session.get(Product, product_id)
    quantity = request.form.get("quantity", 0, type=int)
    cart = _cart()
    if not product or quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = min(quantity, product.stock_quantity)
    session.modified = True
    return redirect(url_for("cart.view"))


@bp.post("/remove/<int:product_id>")
def remove(product_id):
    _cart().pop(str(product_id), None)
    session.modified = True
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart.view"))
