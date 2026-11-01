"""Product catalog.

To add another book later: add one entry here, drop its PDF into files/
and its cover image into app/static/img/, and (optionally) point price_env
at a new env var. Everything else — storefront, checkout, delivery — is
already generic.
"""
import os
from decimal import Decimal, InvalidOperation

PRODUCTS = {
    "princess-fairy-baby-dragon": {
        "title": "The Princess, the Fairy, and the Baby Dragon",
        "author": "Charity Lynn Yancey",
        "ages": "Ages 2–5",
        "blurb": (
            "Princess Poppy loves twirling, singing, and strawberry cake. "
            "Pippa the tiny fairy sprinkles sparkles wherever she flutters. "
            "And Bramble the baby dragon has a problem — when he tries to "
            "breathe fire, only glitter comes out! Join the three friends on "
            "a gentle, giggly adventure through the Whispering Meadow, across "
            "the Giggling Brook, and up the Sleepy Mountain to help Bramble "
            "find his fire. A cozy bedtime story about friendship and helping "
            "each other shine."
        ),
        "details": "12-page full-color picture book · PDF ebook · yours to keep and re-read",
        "cover": "img/cover.webp",
        "file": "princess-fairy-baby-dragon.pdf",
        "download_name": "The-Princess-the-Fairy-and-the-Baby-Dragon.pdf",
        # Price comes from this env var so it can be changed without a code edit.
        "price_env": "STORE_PRICE_USD",
        "default_price": "4.99",
    },
}


def get_product(slug):
    return PRODUCTS.get(slug)


def price_usd(product):
    """Current price for a product as a Decimal, from its env var."""
    raw = os.environ.get(product["price_env"], product["default_price"])
    try:
        return Decimal(raw)
    except InvalidOperation:
        return Decimal(product["default_price"])


def price_cents(product):
    return int((price_usd(product) * 100).to_integral_value())


def price_display(product):
    return f"${price_usd(product):.2f}"
