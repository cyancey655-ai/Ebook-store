"""Stripe Checkout integration.

All secrets come from env via the Flask config. When no secret key is set,
every function raises CheckoutNotConfigured so routes can show the
"checkout not configured yet" state instead of failing.

Checkout uses inline price_data, so no Stripe product/price objects need
to be created in the dashboard ahead of time — Stripe builds the line
item from the name, description, and amount we send.
"""
import stripe


class CheckoutNotConfigured(RuntimeError):
    pass


def _client(config):
    key = config["STRIPE_SECRET_KEY"]
    if not key:
        raise CheckoutNotConfigured("Stripe is not configured.")
    stripe.api_key = key
    # Her Stripe account has Managed Payments enabled, which requires
    # API version 2025-03-31.basil or greater (the SDK default is older).
    stripe.api_version = "2025-03-31.basil"
    return stripe


def create_checkout_session(config, product, slug, unit_amount_cents):
    """Create a one-time-payment Stripe Checkout Session for a product."""
    _client(config)
    base = config["APP_BASE_URL"]
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": "usd",
                    "unit_amount": unit_amount_cents,
                    "product_data": {
                        "name": product["title"],
                        "description": f"Ebook (PDF) by {product['author']} · {product['ages']}",
                        # Managed Payments on her account requires a tax code.
                        "tax_code": config["STRIPE_TAX_CODE"],
                    },
                },
            }
        ],
        success_url=f"{base}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base}/cancel",
        metadata={"product_slug": slug},
        payment_intent_data={"metadata": {"product_slug": slug}},
    )
    return session


def retrieve_checkout_session(config, session_id):
    """Fetch a Checkout Session so /success can verify payment server-side."""
    _client(config)
    return stripe.checkout.Session.retrieve(session_id)
