from flask import Blueprint, render_template
from sqlalchemy import select

from .. import db
from ..models import Category, Product

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    categories = db.session.scalars(
        select(Category).where(Category.is_active.is_(True)).limit(6)
    ).all()
    featured = db.session.scalars(
        select(Product).where(Product.is_active.is_(True), Product.stock_quantity > 0)
        .order_by(Product.created_at.desc()).limit(8)
    ).all()
    return render_template("home.html", categories=categories, featured=featured)
