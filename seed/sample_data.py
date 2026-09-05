import sys
from pathlib import Path

# This script is intentionally runnable as `python seed\\sample_data.py`.
# Python otherwise adds only the seed directory to sys.path, not the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from app.models import AdminUser, Category, Product

app = create_app()
with app.app_context():
    if not Category.query.first():
        cute = Category(name="Cute & Kawaii", slug="cute-kawaii", description="Happy little stickers")
        laptop = Category(name="Laptop Decals", slug="laptop-decals", description="Make your devices yours")
        db.session.add_all([cute, laptop]); db.session.flush()
        db.session.add_all([
            Product(name="Happy Cat", slug="happy-cat", description="Weather-resistant smiling cat sticker.", price=79, stock_quantity=25, category_id=cute.id),
            Product(name="Coffee Club", slug="coffee-club", description="For people powered by coffee.", price=99, stock_quantity=18, category_id=laptop.id),
            Product(name="Rainbow Pack", slug="rainbow-pack", description="A colourful mini sticker pack.", price=149, stock_quantity=12, category_id=cute.id),
        ])
    if not AdminUser.query.first():
        admin = AdminUser(email=app.config["ADMIN_EMAIL"].lower()); admin.set_password(app.config["ADMIN_PASSWORD"]); db.session.add(admin)
    db.session.commit()
    print("Sample catalog and admin account are ready.")
