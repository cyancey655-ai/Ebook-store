"""Central configuration. Every secret comes from the environment — never hardcode."""
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILES_DIR = os.path.join(BASE_DIR, "files")


class Config:
    # Flask — also used to sign download tokens, so keep it secret in production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # Public base URL of the deployed app, e.g. https://ebook-store.onrender.com
    # Used for Stripe success/cancel redirect URLs.
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000").rstrip("/")

    # --- Stripe ---
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    # Her Stripe account has Managed Payments enabled; Checkout product data
    # needs a tax code (same general code her chat app uses).
    STRIPE_TAX_CODE = os.environ.get("STRIPE_TAX_CODE", "txcd_10000000")

    # How long a post-purchase download link stays valid, in seconds (default 24h).
    DOWNLOAD_TOKEN_MAX_AGE = int(os.environ.get("DOWNLOAD_TOKEN_MAX_AGE", "86400"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SECURE_COOKIES", "0") == "1"

    @property
    def stripe_configured(self):
        return bool(self.STRIPE_SECRET_KEY)
