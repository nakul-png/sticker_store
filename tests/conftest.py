import pytest

from app import create_app, db
from app.models import Category, Product


@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}", "SECRET_KEY": "test", "PAYMENT_KEY_ID": "", "PAYMENT_KEY_SECRET": ""})
    with app.app_context():
        db.create_all()
        category = Category(name="Test", slug="test")
        db.session.add(category); db.session.flush()
        db.session.add(Product(name="Test sticker", slug="test-sticker", description="A test sticker", price=99, stock_quantity=3, category_id=category.id))
        db.session.commit()
        yield app
        db.session.remove(); db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
