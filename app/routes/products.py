from flask import Blueprint, abort, render_template, request
from sqlalchemy import or_, select

from .. import db
from ..models import Category, Product

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.get("/")
def listing():
    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip()
    sort = request.args.get("sort", "newest")
    stmt = select(Product).where(Product.is_active.is_(True))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.description.ilike(like)))
    if category_slug:
        stmt = stmt.join(Product.category).where(Category.slug == category_slug)
    orderings = {"price_asc": Product.price.asc(), "price_desc": Product.price.desc(), "name": Product.name.asc(), "newest": Product.created_at.desc()}
    products = db.session.scalars(stmt.order_by(orderings.get(sort, Product.created_at.desc()))).all()
    categories = db.session.scalars(select(Category).where(Category.is_active.is_(True)).order_by(Category.name)).all()
    return render_template("products/list.html", products=products, categories=categories, q=q, selected_category=category_slug, sort=sort)


@bp.get("/<slug>")
def detail(slug):
    product = db.session.scalar(select(Product).where(Product.slug == slug, Product.is_active.is_(True)))
    if not product:
        abort(404)
    related = db.session.scalars(select(Product).where(Product.category_id == product.category_id, Product.id != product.id, Product.is_active.is_(True)).limit(4)).all()
    return render_template("products/detail.html", product=product, related=related)
