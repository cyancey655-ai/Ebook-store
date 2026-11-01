# Charity's Ebook Store

A small, real online shop where Charity sells her children's ebook from her
**own** website — no Amazon, no eBay. Buyers pay through Stripe Checkout
(using Charity's existing Stripe account) and get their PDF download right
after payment is verified.

**First book:** *The Princess, the Fairy, and the Baby Dragon* by Charity Lynn
Yancey — a 12-page full-color picture book for ages 2–5, with Princess Poppy,
Pippa the fairy, and Bramble the baby dragon.

## What was built

| Piece | Where |
|---|---|
| Storefront (cover, blurb, ages, price, buy button) | `app/routes.py` → `/`, `app/templates/index.html` |
| Product catalog (add more books here later) | `app/products.py` |
| Real Stripe Checkout session creation | `app/payments.py`, route `POST /buy/<slug>` |
| Payment verification before delivery | route `GET /success` |
| Signed, expiring download links | `app/downloads.py`, route `GET /download/<token>` |
| The ebook file itself | `files/princess-fairy-baby-dragon.pdf` |
| All settings/secrets from environment | `app/config.py`, `.env.example` |
| Render deploy config (free tier, same shape as amani-chat-app) | `render.yaml`, `Procfile`, `wsgi.py` |

### How buying works

1. Buyer clicks **Buy now** → the app creates a real Stripe Checkout Session
   and sends them to Stripe's payment page.
2. **No Stripe product or price needs to be created in the dashboard** — the
   app sends the book's name, description, and amount inline (`price_data`)
   with each checkout, including the tax code her Managed Payments account
   requires.
3. Stripe sends the buyer back to `/success`. The app asks Stripe directly
   (server-side) whether that session's `payment_status` is really `paid`.
   No webhook is needed, and nobody can fake their way to a download by
   just visiting the success page.
4. Only after Stripe confirms payment does the buyer see a download button.
   The link contains a signed token that expires (24 hours by default), so
   the PDF is never sitting at a public, permanent, guessable URL.

### Graceful "not configured" mode

If `STRIPE_SECRET_KEY` is not set, the whole shop still runs: pages render,
the book and price show, but the buy button is disabled and reads
**"Checkout not configured yet."** Nothing is faked — checkout simply isn't
live until the real key is in place.

## Run it locally

```bash
cd ~/workspace/ebook-store
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optional; defaults work without it
python wsgi.py              # then open http://localhost:5000
```

Environment variables (see `.env.example` for the full list):

- `SECRET_KEY` — signs download tokens; long random string in production.
- `APP_BASE_URL` — public URL of the deployed app (Stripe redirect target).
- `STRIPE_SECRET_KEY` — secret key from Charity's Stripe account. Empty = shop runs in "not configured" mode.
- `STORE_PRICE_USD` — book price. **Currently the placeholder $4.99.**
- `STRIPE_TAX_CODE` — defaults to `txcd_10000000` (same code her chat app uses).
- `DOWNLOAD_TOKEN_MAX_AGE` — download-link lifetime in seconds (default 86400 = 24h).

## ⚠️ Remaining steps — these need Charity

The code is finished and tested locally. Going live needs these, in order:

1. **Confirm the price.** The shop currently shows **$4.99** as a placeholder.
   Charity picks the real price; it's set with the `STORE_PRICE_USD` env var —
   no code change needed.
2. **Create a GitHub repo** for this folder (e.g. `ebook-store`) and push the
   code, same as the amani-chat-app repo. (Heads-up: the ebook PDF is ~76 MB,
   so the first push is slow, and GitHub will show a large-file warning — it's
   under GitHub's 100 MB per-file limit, so it still works. A smaller,
   compressed PDF can be swapped in later without any code change.)
3. **Create the Render service**: New → Web Service (or Blueprint using the
   included `render.yaml`), connect the new repo. Free tier, same as the chat
   app. Set `APP_BASE_URL` to the new service's `https://….onrender.com` URL.
4. **Paste the Stripe secret key**: in the Render service's Environment tab,
   set `STRIPE_SECRET_KEY` to the live secret key from her existing Stripe
   account (the "Armani" one). Nothing new needs to be created in Stripe —
   no product, no price, no webhook.
5. **Manual Deploy** → "Deploy latest commit" (her Render services don't
   auto-deploy after changes).
6. **One real test purchase** with her own card to prove the full loop:
   pay → land on the success page → download link works → PDF opens.
   (Same style of careful end-to-end check the chat site still needs.)

Until step 4 is done, the deployed shop will simply show the
"Checkout not configured yet" state — safe to deploy early and share the link.

## Adding another book later

Add one entry to `PRODUCTS` in `app/products.py`, drop the PDF in `files/`
and the cover in `app/static/img/`, redeploy. Storefront, checkout, payment
verification, and expiring downloads all work for it automatically.
