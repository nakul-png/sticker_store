# PERSONAA

A mobile-friendly Flask e-commerce MVP for stickers. It uses SQLite locally, server-side cart totals, CSRF protection, password-hashed admin access, safe image uploads and a Razorpay-ready checkout.

## Run locally (Windows)

1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/) and tick **Add Python to PATH**.
2. In this folder, run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   python seed\sample_data.py
   python app.py
   ```
3. Visit `http://127.0.0.1:5000`. The sample admin uses the `ADMIN_EMAIL` and `ADMIN_PASSWORD` values in your local `.env`; change both before use.

## Tests

```powershell
pytest
```

## Payment and email behaviour

With no payment keys, checkout creates a **pending** order and never pretends that it is paid. Add Razorpay sandbox credentials to `.env` to enable its hosted checkout. The backend verifies the returned HMAC signature before marking an order paid and reducing stock.

With no SMTP configuration, order email content is logged safely instead of causing checkout failure.

## Deploy cheaply

Develop and test locally at ₹0. For a small live store, choose one Flask-compatible host and a domain only when ready. Set production environment variables in the host dashboard, use Gunicorn, set `FLASK_ENV=production`, migrate from SQLite to a managed PostgreSQL database if concurrent orders grow, and use object storage if host uploads are ephemeral. See `MANUAL_ACTIONS.md` before launch.

Never commit `.env`, real customer databases, payment secrets or SMTP passwords.
