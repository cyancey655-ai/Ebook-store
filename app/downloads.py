"""Signed, expiring download tokens.

After Stripe confirms a payment, /success mints one of these tokens and
the download link carries it. The ebook file itself is never exposed at a
public permanent URL: /download/<token> only serves the file when the
token's signature checks out and it hasn't expired.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SALT = "ebook-download"


def _serializer(secret_key):
    return URLSafeTimedSerializer(secret_key, salt=SALT)


def make_download_token(secret_key, slug, session_id):
    return _serializer(secret_key).dumps({"slug": slug, "session": session_id})


def read_download_token(secret_key, token, max_age):
    """Return the token payload, or raise BadSignature / SignatureExpired."""
    return _serializer(secret_key).loads(token, max_age=max_age)


__all__ = [
    "BadSignature",
    "SignatureExpired",
    "make_download_token",
    "read_download_token",
]
