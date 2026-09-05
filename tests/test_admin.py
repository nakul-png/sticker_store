from app import db
from app.models import AdminUser


def test_admin_routes_require_login(client):
    assert client.get("/admin/", follow_redirects=False).status_code == 302


def test_admin_login(client, app):
    with app.app_context():
        user = AdminUser(email="admin@test.com"); user.set_password("password")
        db.session.add(user); db.session.commit()
    response = client.post("/admin/login", data={"email":"admin@test.com","password":"password"}, follow_redirects=True)
    assert b"Dashboard" in response.data
