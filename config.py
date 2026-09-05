import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def database_url():
    """Return a stable absolute SQLite URL, even when launched from VS Code."""
    configured = os.getenv("DATABASE_URL", "").strip()
    if configured.startswith("sqlite:///"):
        sqlite_path = configured.removeprefix("sqlite:///")
        # A relative URL in .env should be relative to this project, not the
        # terminal's current directory.
        if sqlite_path and not Path(sqlite_path).is_absolute() and not (len(sqlite_path) > 1 and sqlite_path[1] == ":"):
            return f"sqlite:///{(BASE_DIR / sqlite_path).resolve().as_posix()}"
    return configured or f"sqlite:///{(BASE_DIR / 'instance' / 'store.db').as_posix()}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    # SQLAlchemy SQLite URLs need forward slashes on Windows too.  A raw
    # pathlib Windows path (D:\\...) can be parsed incorrectly and produces
    # "unable to open database file".
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    PAYMENT_KEY_ID = os.getenv("PAYMENT_KEY_ID", "")
    PAYMENT_KEY_SECRET = os.getenv("PAYMENT_KEY_SECRET", "")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-this-before-first-run")
    STORE_NAME = os.getenv("STORE_NAME", "Sticker Studio")
    SHIPPING_FLAT_RATE = int(os.getenv("SHIPPING_FLAT_RATE", "49"))
    FREE_SHIPPING_THRESHOLD = int(os.getenv("FREE_SHIPPING_THRESHOLD", "499"))
    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "products"
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
