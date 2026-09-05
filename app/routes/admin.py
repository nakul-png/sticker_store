from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, select

from .. import db
from ..models import AdminUser, Category, Order, Product
from ..services.image_service import save_image

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


def make_slug(value):
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    return "-".join(filter(None, cleaned.split("-")))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.session.scalar(select(AdminUser).where(AdminUser.email == request.form.get("email", "").strip().lower()))
        if user and user.check_password(request.form.get("password", "")):
            session.clear()
            session["admin_id"] = user.id
            return redirect(url_for("admin.dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("admin/login.html")


@bp.post("/logout")
@admin_required
def logout():
    session.clear()
    return redirect(url_for("main.home"))


@bp.get("/")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", product_count=db.session.scalar(select(func.count(Product.id))), order_count=db.session.scalar(select(func.count(Order.id))), low_stock=db.session.scalars(select(Product).where(Product.stock_quantity < 5, Product.is_active.is_(True))).all())


@bp.route("/products", methods=["GET", "POST"])
@admin_required
def products():
    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id", type=int)
        price = request.form.get("price", type=float)
        stock = request.form.get("stock_quantity", type=int)
        if not name or not category_id or price is None or price < 0 or stock is None or stock < 0:
            flash("Name, category, valid price and stock are required.", "error")
        else:
            slug_base, suffix = make_slug(name), 1
            slug = slug_base
            while db.session.scalar(select(Product).where(Product.slug == slug)):
                suffix += 1; slug = f"{slug_base}-{suffix}"
            try:
                image_url = save_image(request.files.get("image"))
                db.session.add(Product(name=name, slug=slug, description=request.form.get("description", "").strip(), category_id=category_id, price=price, stock_quantity=stock, image_url=image_url))
                db.session.commit(); flash("Product created.", "success")
                return redirect(url_for("admin.products"))
            except ValueError as exc:
                flash(str(exc), "error")
    return render_template("admin/products.html", products=db.session.scalars(select(Product).order_by(Product.created_at.desc())).all(), categories=categories)


@bp.post("/products/<int:product_id>/toggle")
@admin_required
def product_toggle(product_id):
    product = db.session.get(Product, product_id)
    if product:
        product.is_active = not product.is_active; db.session.commit()
    return redirect(url_for("admin.products"))


@bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = make_slug(name)
        if not name or db.session.scalar(select(Category).where(Category.slug == slug)):
            flash("Enter a unique category name.", "error")
        else:
            db.session.add(Category(name=name, slug=slug, description=request.form.get("description", "").strip())); db.session.commit(); flash("Category created.", "success")
            return redirect(url_for("admin.categories"))
    return render_template("admin/categories.html", categories=db.session.scalars(select(Category).order_by(Category.name)).all())


@bp.get("/orders")
@admin_required
def orders():
    return render_template("admin/orders.html", orders=db.session.scalars(select(Order).order_by(Order.created_at.desc())).all())


@bp.post("/orders/<int:order_id>/status")
@admin_required
def order_status(order_id):
    order = db.session.get(Order, order_id)
    status = request.form.get("order_status")
    if order and status in {"pending", "confirmed", "processing", "shipped", "delivered", "cancelled"}:
        order.order_status = status; db.session.commit(); flash("Order status updated.", "success")
    return redirect(url_for("admin.orders"))
