"""Storefront, checkout, payment verification, and download delivery."""
import os

import stripe
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from itsdangerous import BadSignature, SignatureExpired

from . import downloads, payments, products
from .config import FILES_DIR

bp = Blueprint("store", __name__)


def _catalog():
    """Storefront view of every product, with live prices."""
    items = []
    for slug, product in products.PRODUCTS.items():
        items.append(
            {
                "slug": slug,
                "product": product,
                "price": products.price_display(product),
            }
        )
    return items


@bp.route("/")
def index():
    return render_template(
        "index.html",
        catalog=_catalog(),
        checkout_ready=current_app.config["STRIPE_SECRET_KEY"] != "",
    )


@bp.route("/buy/<slug>", methods=["POST"])
def buy(slug):
    product = products.get_product(slug)
    if product is None:
        abort(404)
    if not current_app.config["STRIPE_SECRET_KEY"]:
        flash("Checkout isn't set up yet — please check back soon!", "info")
        return redirect(url_for("store.index"))
    try:
        session = payments.create_checkout_session(
            current_app.config,
            product,
            slug,
            products.price_cents(product),
        )
    except stripe.error.StripeError:
        flash(
            "Sorry — checkout hit a snag. Please try again in a little while.",
            "error",
        )
        return redirect(url_for("store.index"))
    return redirect(session.url, code=303)


@bp.route("/success")
def success():
    session_id = request.args.get("session_id", "")
    if not session_id:
        return render_template(
            "message.html",
            title="Hmm, no order found",
            message=(
                "We couldn't find a payment to check. If you just bought the "
                "book, please use the download link from your checkout — or "
                "head back to the shop and try again."
            ),
        )
    if not current_app.config["STRIPE_SECRET_KEY"]:
        return render_template(
            "message.html",
            title="Checkout isn't set up yet",
            message="This shop isn't taking payments yet — please check back soon!",
        )
    try:
        session = payments.retrieve_checkout_session(current_app.config, session_id)
    except stripe.error.StripeError:
        return render_template(
            "message.html",
            title="We couldn't verify that payment",
            message=(
                "Something went wrong while checking your payment with Stripe. "
                "If your card was charged, please don't buy again — reach out "
                "and we'll sort it out."
            ),
        )
    slug = (session.metadata or {}).get("product_slug", "")
    product = products.get_product(slug)
    if product is None or session.payment_status != "paid":
        return render_template(
            "message.html",
            title="Payment not completed",
            message=(
                "It doesn't look like that payment went through, so there's "
                "nothing to download yet. Your card has not been charged for "
                "an unfinished checkout."
            ),
        )
    token = downloads.make_download_token(
        current_app.config["SECRET_KEY"], slug, session.id
    )
    hours = max(1, current_app.config["DOWNLOAD_TOKEN_MAX_AGE"] // 3600)
    return render_template(
        "success.html",
        product=product,
        download_url=url_for("store.download", token=token),
        valid_hours=hours,
    )


@bp.route("/cancel")
def cancel():
    return render_template("cancel.html")


@bp.route("/download/<token>")
def download(token):
    try:
        payload = downloads.read_download_token(
            current_app.config["SECRET_KEY"],
            token,
            current_app.config["DOWNLOAD_TOKEN_MAX_AGE"],
        )
    except SignatureExpired:
        return render_template(
            "message.html",
            title="That download link has expired",
            message=(
                "Download links are only good for a little while to keep the "
                "book safe. If you're the buyer, please check your email "
                "receipt or get in touch and we'll send a fresh link."
            ),
        ), 403
    except BadSignature:
        abort(404)
    product = products.get_product(payload.get("slug", ""))
    if product is None:
        abort(404)
    path = os.path.join(FILES_DIR, product["file"])
    if not os.path.isfile(path):
        abort(404)
    return send_file(
        path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=product["download_name"],
    )


@bp.route("/healthz")
def healthz():
    return "ok", 200
