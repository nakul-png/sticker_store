from pathlib import Path

from flask import Blueprint, current_app, render_template, url_for
from sqlalchemy import select

from .. import db
from ..models import Category, Product

bp = Blueprint("main", __name__)


def _static_asset_url(relative_path):
    """Return a static URL only when the owner has supplied that asset."""
    asset = Path(current_app.static_folder) / relative_path
    return url_for("static", filename=relative_path) if asset.is_file() else ""


@bp.get("/")
def home():
    categories = db.session.scalars(
        select(Category).where(Category.is_active.is_(True)).limit(6)
    ).all()
    featured = db.session.scalars(
        select(Product).where(Product.is_active.is_(True), Product.stock_quantity > 0)
        .order_by(Product.created_at.desc()).limit(8)
    ).all()
    hero_assets = {
        "webm": _static_asset_url("videos/hero/personaa-hero.webm"),
        "mp4": _static_asset_url("videos/hero/personaa-hero.mp4"),
        "poster": _static_asset_url("videos/hero/personaa-hero-poster.webp"),
        "model": _static_asset_url("models/hero/personaa-hero.glb"),
    }
    return render_template(
        "home.html", categories=categories, featured=featured, hero_assets=hero_assets
    )
