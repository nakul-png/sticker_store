# Owner-only setup checklist

Everything below requires your account, private credentials, KYC, a purchase, real business data, or a policy decision. Do **not** paste secrets into chat or commit them to Git.

## Before local testing

1. Install Python 3.11+ and run the commands in `README.md`.
2. Copy `.env.example` to `.env` and set a long random `SECRET_KEY`.
3. Set a unique `ADMIN_EMAIL` and `ADMIN_PASSWORD`; run the seed script once.

## Before sandbox payment testing

1. Create your own Razorpay account and complete any test-account requirements.
2. Create test API keys in Razorpay, then put `PAYMENT_KEY_ID` and `PAYMENT_KEY_SECRET` only in local `.env`.
3. Use Razorpay's test method to place a controlled order. Confirm it is marked paid only after server-side verification.

## Before launch

1. Decide your final brand/store name and add it as `STORE_NAME`.
2. Add real product names, descriptions, prices, stock, categories, and compressed WebP/JPEG/PNG images through Admin.
3. Decide shipping charges, free-shipping threshold, serviceable locations, return/refund/cancellation policy, and customer contact details.
4. Buy/register a domain and choose a Flask-compatible host. Domain and hosting are expected costs; check current pricing yourself before purchasing.
5. Create a merchant payment account, complete KYC, then place live credentials only in the host's environment-variable/secret manager.
6. Create/verify a sender email account; add SMTP settings only in the host's secret manager.
7. Configure DNS and HTTPS at the host; set `FLASK_ENV=production`, disable debug, and create a strong production admin password.
8. Confirm the host has persistent uploads. If not, configure object storage before accepting real product-image uploads.
9. Take a database backup, place one controlled live order, verify the payment/order email/admin workflow, then launch.

## Cost intent

- Development: ₹0 (Flask, SQLite, HTML/CSS/JS, Git).
- Launch: domain plus hosting are the planned costs. SSL is often included; verify the host's current terms.
- Sales: payment gateways charge transaction fees; email/storage/database upgrades should wait for real need.
