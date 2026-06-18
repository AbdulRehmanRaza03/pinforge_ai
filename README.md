# 📌 PinForge AI

Safe, ethical, production-ready Pinterest automation SaaS. Built entirely on the
**official Pinterest API v5** with OAuth2 — no scraping, no headless browsers,
no ToS-violating automation.

## Why it's safe

| Risk | How PinForge AI handles it |
|---|---|
| Spam-like posting | Hard cap: max **15 pins/account/day** (configurable lower, never higher) |
| Bot-like cadence | Randomized **15–60 minute** delay injected between every post |
| Duplicate content | SHA-256 content hash blocks re-posting identical title+description to the same account |
| Credential leaks | Zero hardcoded secrets — everything via `.env` / environment variables |
| Unauthorized access | Every account connection goes through Pinterest's standard OAuth2 consent screen |
| Silent failures | Every single post attempt (success, failure, skipped) is logged to `post_history` |

## Project structure

```
pinforge_ai/
├── app.py              # Streamlit UI + routing
├── config.py           # Env-driven settings, hard safety caps
├── models.py           # SQLAlchemy models (User, PinterestAccount, Queue, History)
├── database.py         # Engine/session setup
├── pinterest_api.py    # Official Pinterest API v5 OAuth2 + endpoints wrapper
├── ai_engine.py         # Claude-powered title/description/hashtag/alt-text generation
├── image_processor.py  # Pillow resize to Pinterest 2:3 ratio, EXIF strip
├── scheduler.py        # APScheduler background job: enforces all safety rules
├── utils.py             # Hashing, randomized delay, validators, logging
├── requirements.txt
├── .env.example
└── static/
    ├── uploads/
    └── processed/
```

## Setup

```bash
git clone <your-fork-url> pinforge_ai
cd pinforge_ai
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then fill in real values
```

### 1. Create a Pinterest Developer App
1. Go to https://developers.pinterest.com/apps/ and create an app.
2. Add redirect URI: `http://localhost:8501` (or your deployed URL).
3. Request scopes: `boards:read, boards:write, pins:read, pins:write, user_accounts:read`.
4. Copy **App ID** and **App Secret** into `.env`.

### 2. Get an Anthropic API key
Create one at https://console.anthropic.com → put it in `ANTHROPIC_API_KEY`.

### 3. Run locally
```bash
streamlit run app.py
```
Open http://localhost:8501, sign up, click **Connect Pinterest Account**, approve access, start queuing pins.

## Environment variables

| Variable | Required | Notes |
|---|---|---|
| `SECRET_KEY` | yes | long random string |
| `DATABASE_URL` | yes | defaults to local SQLite; use Postgres in production |
| `PINTEREST_APP_ID` / `PINTEREST_APP_SECRET` | yes | from Pinterest developer dashboard |
| `PINTEREST_REDIRECT_URI` | yes | must exactly match what's registered with Pinterest |
| `ANTHROPIC_API_KEY` | yes | powers AI content generation |
| `MAX_PINS_PER_ACCOUNT_PER_DAY` | no | hard-capped at 15 regardless of value set higher |
| `MIN_DELAY_MINUTES` / `MAX_DELAY_MINUTES` | no | hard floor 15 / hard ceiling 120 |

## Deployment

### Streamlit Community Cloud
1. Push repo to GitHub.
2. New app on https://share.streamlit.io → point at `app.py`.
3. Add all `.env` values under **Settings → Secrets** as TOML:
   ```toml
   PINTEREST_APP_ID = "..."
   PINTEREST_APP_SECRET = "..."
   ANTHROPIC_API_KEY = "..."
   PINTEREST_REDIRECT_URI = "https://yourapp.streamlit.app"
   ```
4. Update the redirect URI in your Pinterest app settings to match.

### Render
1. New **Web Service** → connect repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add environment variables in the Render dashboard (same keys as `.env`).
5. For persistence beyond the free tier's ephemeral disk, switch `DATABASE_URL` to a managed Postgres instance (Render offers one).

### Railway
1. New project → deploy from GitHub repo.
2. Railway auto-detects Python; set start command to:
   `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. Add environment variables in **Variables** tab.
4. Attach a Railway Postgres plugin and set `DATABASE_URL` to its connection string for production durability.

## Operational notes
- The background scheduler (APScheduler) only runs while the Streamlit process is alive — for a long-running production queue, deploy as a persistent service (Render/Railway, not a serverless function).
- Pinterest API rate limits and terms can change; review https://developers.pinterest.com/docs/api/v5/ periodically.
- This tool only ever acts on accounts the user explicitly connects via OAuth, and only posts content the user explicitly queues.
