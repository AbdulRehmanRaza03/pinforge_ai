<div align="center">

<img src="https://img.shields.io/badge/PinForge_AI-v1.0.0-9333ea?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJDOC4xMyAyIDUgNS4xMyA1IDljMCAzLjU0IDIuNjEgNi40NiA2IDYuOTNWMjNoMnYtNi4wN2MzLjM5LS40NyA2LTMuMzkgNi02LjkzIDAtMy44Ny0zLjEzLTctNy03eiIvPjwvc3ZnPg==" alt="PinForge AI" />

# PinForge AI

### Pinterest Automation SaaS — Built on Official API v5

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ecf8e?style=flat-square&logo=supabase)](https://supabase.com)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square&logo=vercel)](https://vercel.com)
[![Railway](https://img.shields.io/badge/Backend-Railway-7c3aed?style=flat-square)](https://railway.app)
[![Pinterest API](https://img.shields.io/badge/Pinterest-API_v5_Official-e60023?style=flat-square&logo=pinterest)](https://developers.pinterest.com/docs/api/v5/)
[![License](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](LICENSE)

**Schedule, automate, and AI-optimize your Pinterest pins.  
No bots. No scraping. 100% official Pinterest API v5.**

[Live Demo](#) · [Report Bug](issues) · [Request Feature](issues) · [Phase 2 Roadmap](#phase-2-roadmap)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Safety & Ethics](#safety--ethics)
- [Required API Keys](#required-api-keys)
- [Local Development Setup](#local-development-setup)
- [Supabase Setup](#supabase-setup)
- [Pinterest Developer App Setup](#pinterest-developer-app-setup)
- [AI API Keys Setup](#ai-api-keys-setup)
- [Running Locally](#running-locally)
- [Deployment — Vercel (Frontend)](#deployment--vercel-frontend)
- [Deployment — Railway (Backend)](#deployment--railway-backend)
- [Environment Variables Reference](#environment-variables-reference)
- [Project Structure](#project-structure)
- [Phase 2 Roadmap](#phase-2-roadmap)
- [Contributing](#contributing)

---

## Overview

PinForge AI is a multi-user SaaS platform that lets creators, affiliate marketers, and e-commerce brands:

- **Upload product images** (single or bulk, JPG/PNG/WEBP up to 20MB)
- **AI-generate pin content** — title, description, hashtags, alt text (Gemini / OpenAI / DeepSeek)
- **Connect multiple Pinterest business accounts** via official OAuth2
- **Schedule pins with human-like delays** (15–60 min randomized gaps, 15 pins/day cap)
- **Track posting history and analytics** per account
- **Manage queues** — add, remove, preview scheduled pins

---

## Architecture

```
┌────────────────────┐       ┌──────────────────────┐       ┌─────────────────┐
│  Next.js 14        │  ───▶ │  FastAPI Backend      │  ───▶ │  Pinterest      │
│  (Vercel)          │       │  (Railway)            │       │  API v5         │
│                    │       │                       │       └─────────────────┘
│  • Landing page    │       │  • Pinterest OAuth    │
│  • Auth (Supabase) │       │  • AI content gen     │       ┌─────────────────┐
│  • Dashboard       │       │  • Image processing   │  ───▶ │  Gemini / OpenAI│
│  • Create pins     │       │  • Background sched.  │       │  / DeepSeek     │
│  • Queue view      │       │  • Safety enforcement │       └─────────────────┘
│  • Analytics       │       │  • Rate limiting      │
│  • Settings        │       └──────────────────────┘       ┌─────────────────┐
└────────────────────┘                │                      │  Supabase       │
                                      └─────────────────────▶│  • Auth / JWT   │
                                                             │  • PostgreSQL   │
                                                             └─────────────────┘
```

**OAuth2 Flow:**
```
User → "Connect Pinterest" → Backend generates auth URL
→ Pinterest consent screen → Approves
→ Pinterest → Backend /callback (exchanges code for tokens)
→ Tokens stored in DB → Redirects user to dashboard
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14 (App Router) | SSR, file-based routing, production-ready |
| UI | Tailwind CSS + Framer Motion | Custom design tokens, smooth animations |
| Charts | Recharts | Flexible, composable data visualization |
| Backend | FastAPI (Python) | Fast, async, auto-generates OpenAPI docs |
| Auth | Supabase Auth | JWT-based, handles sessions, free tier |
| Database | Supabase PostgreSQL | Managed Postgres, Row Level Security |
| ORM | SQLAlchemy 2.0 | Production-tested, Postgres-ready |
| Scheduler | APScheduler | Background jobs without a separate worker |
| AI | Gemini 1.5 Flash / GPT-4o Mini / DeepSeek | Multi-provider, user brings own key |
| Images | Pillow | Pinterest 2:3 crop, EXIF strip, JPEG optimize |
| API | Pinterest API v5 (official) | No ToS violations, OAuth2 tokens only |
| Frontend deploy | Vercel | Free tier, automatic CI/CD from GitHub |
| Backend deploy | Railway | $5/month, persistent, auto-deploy from GitHub |

---

## Safety & Ethics

PinForge AI is designed to keep your Pinterest account safe:

| Safety Rule | Implementation |
|-------------|---------------|
| **Max 15 pins/day per account** | Hard cap enforced in `config.py` — cannot be bypassed via UI or env vars |
| **Human-like delay 15–60 min** | Random delay injected on every `enqueue_pin()` call |
| **No duplicate content** | SHA-256 hash of title+description blocks re-posting |
| **Official API only** | Only `api.pinterest.com/v5` endpoints — no scraping, no headless browsers |
| **OAuth2 tokens only** | Never stores Pinterest passwords — only the access token Pinterest issues |
| **Full audit trail** | Every post attempt (success/fail/skip) logged to `post_history` table |
| **User-initiated actions** | Scheduler only posts what the user explicitly queued |

---

## Required API Keys

You need **4 things** to run PinForge AI:

| # | Service | Key Type | Required |
|---|---------|----------|----------|
| 1 | **Supabase** | URL + Anon Key + Service Key + JWT Secret | ✅ Yes |
| 2 | **Pinterest Developer App** | App ID + App Secret | ✅ Yes |
| 3 | **Gemini** | API Key | ✅ Yes (for AI generation — free tier works) |
| 4 | **OpenAI** | API Key | Optional |

---

## Local Development Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/pinforge-ai.git
cd pinforge-ai
```

---

## Supabase Setup

### Step 1 — Create project

1. Go to [supabase.com](https://supabase.com) → **New project**
2. Choose a name (e.g. `pinforge-ai`) and a strong database password
3. Select the region closest to your users
4. Wait ~2 minutes for the project to provision

### Step 2 — Get your keys

Go to **Settings → API** in your Supabase project dashboard:

| Key | Where to find it |
|-----|-----------------|
| `SUPABASE_URL` | "Project URL" field |
| `NEXT_PUBLIC_SUPABASE_URL` | Same as above |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | "anon public" key |
| `SUPABASE_SERVICE_KEY` | "service_role" key (keep secret!) |
| `SUPABASE_JWT_SECRET` | **Settings → API → JWT Settings → JWT Secret** |

### Step 3 — Get Database URL

Go to **Settings → Database → Connection string → URI** tab.  
Copy the **"Direct connection"** URI (not the pooler).  
Replace `[YOUR-PASSWORD]` with your database password.

```
postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
```

This goes in `DATABASE_URL` in the backend `.env`.

### Step 4 — Enable Email Auth

Go to **Authentication → Providers → Email** — make sure it's enabled (it is by default).

### Step 5 — Tables

Tables are created automatically when you run the backend for the first time (`init_db()` runs on startup). No manual SQL needed.

---

## Pinterest Developer App Setup

### Step 1 — Create app

1. Go to [developers.pinterest.com/apps](https://developers.pinterest.com/apps/)
2. Click **Create app**
3. Fill in app name (e.g. "PinForge AI"), description, contact email
4. Accept the developer terms

### Step 2 — Configure OAuth

In your app settings:
1. Under **Redirect URIs**, add:
   - `http://localhost:8000/api/accounts/callback` (for local dev)
   - `https://your-backend.railway.app/api/accounts/callback` (for production)
2. Under **Scopes**, request all of:
   - `boards:read` `boards:write` `pins:read` `pins:write` `user_accounts:read`

### Step 3 — Get credentials

From the app dashboard, copy:
- **App ID** → `PINTEREST_APP_ID`
- **App secret key** → `PINTEREST_APP_SECRET`

> ⚠️ Pinterest may require your app to go through review to use write scopes in production. In development/sandbox mode you can test with your own Pinterest account.

---

## AI API Keys Setup

### Gemini (Recommended — Free tier)

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API key**
3. Copy the key → `GEMINI_API_KEY`

Free tier: 15 requests/minute, 1500 requests/day — enough for development and light production use.

### OpenAI (Optional)

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **Create new secret key**
3. Copy → `OPENAI_API_KEY`

Uses `gpt-4o-mini` by default (~$0.15/1M input tokens).

### DeepSeek (Optional)

1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Create account → API Keys → Create key
3. Users add this as their personal key in Settings.

---

## Running Locally

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Now edit .env with your real values (Supabase, Pinterest, Gemini keys)

# Create static folders
mkdir -p static/uploads static/processed

# Run the server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local:
#   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
#   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
#   NEXT_PUBLIC_API_URL=http://localhost:8000

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:3000

### First run checklist

- [ ] Backend starts without errors and shows `[PinForge AI] Backend running`
- [ ] http://localhost:8000/health returns `{"status": "ok"}`
- [ ] http://localhost:8000/docs shows the FastAPI Swagger UI
- [ ] Frontend loads at http://localhost:3000
- [ ] Can create an account and log in
- [ ] Pinterest OAuth flow works (connect account)
- [ ] Can upload image, generate AI content, add to queue

---

## Deployment — Vercel (Frontend)

### Step 1 — Push to GitHub

```bash
# From the pinforge-ai root
git init
git add .
git commit -m "feat: initial PinForge AI setup"
git remote add origin https://github.com/yourusername/pinforge-ai.git
git push -u origin main
```

### Step 2 — Import to Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New → Project**
2. Import your GitHub repository
3. Set **Root Directory** to `frontend`
4. Framework preset: **Next.js** (auto-detected)

### Step 3 — Add environment variables

In Vercel project → **Settings → Environment Variables**, add:

```
NEXT_PUBLIC_SUPABASE_URL          = https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY     = eyJhbGc...
NEXT_PUBLIC_API_URL               = https://your-backend.railway.app
```

### Step 4 — Deploy

Click **Deploy**. Vercel builds and gives you a URL like `https://pinforge-ai.vercel.app`.

Every push to `main` auto-redeploys.

---

## Deployment — Railway (Backend)

### Step 1 — Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**
2. Select your `pinforge-ai` repo
3. Set **Root Directory** to `backend`

### Step 2 — Add environment variables

In Railway → your service → **Variables**, add all backend env vars:

```
ENV                       = production
FRONTEND_URL              = https://your-app.vercel.app
DATABASE_URL              = postgresql://postgres:...@db...supabase.co:5432/postgres
SUPABASE_URL              = https://xxxx.supabase.co
SUPABASE_SERVICE_KEY      = eyJhbGc...
SUPABASE_JWT_SECRET       = your-jwt-secret
PINTEREST_APP_ID          = your_app_id
PINTEREST_APP_SECRET      = your_app_secret
PINTEREST_REDIRECT_URI    = https://your-backend.railway.app/api/accounts/callback
GEMINI_API_KEY            = AIzaSy...
DEFAULT_AI_PROVIDER       = gemini
MAX_PINS_PER_ACCOUNT_PER_DAY = 15
MIN_DELAY_MINUTES         = 15
MAX_DELAY_MINUTES         = 60
```

### Step 3 — Start command

Railway auto-detects the `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 4 — Update Pinterest redirect URI

In your Pinterest developer app settings, add the Railway backend URL:
```
https://your-backend.railway.app/api/accounts/callback
```

### Step 5 — Update CORS

Make sure `FRONTEND_URL` in Railway vars is set to your Vercel URL so the backend allows requests from it.

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `ENV` | Yes | `development` or `production` |
| `FRONTEND_URL` | Yes | Your Vercel URL (for CORS + OAuth redirect) |
| `DATABASE_URL` | Yes | Supabase PostgreSQL connection URI |
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase `service_role` key — never expose publicly |
| `SUPABASE_JWT_SECRET` | Yes | From Supabase → Settings → API → JWT Secret |
| `PINTEREST_APP_ID` | Yes | From Pinterest developer dashboard |
| `PINTEREST_APP_SECRET` | Yes | From Pinterest developer dashboard |
| `PINTEREST_REDIRECT_URI` | Yes | Must match exactly what's registered in Pinterest app |
| `GEMINI_API_KEY` | Yes* | For AI generation. *Required if using Gemini (default) |
| `OPENAI_API_KEY` | No | For OpenAI provider |
| `DEFAULT_AI_PROVIDER` | No | `gemini` (default), `openai`, or `deepseek` |
| `MAX_PINS_PER_ACCOUNT_PER_DAY` | No | Default 15, hard max 15 |
| `MIN_DELAY_MINUTES` | No | Default 15, hard min 15 |
| `MAX_DELAY_MINUTES` | No | Default 60, hard max 120 |
| `UPLOAD_DIR` | No | Default `static/uploads` |
| `PROCESSED_DIR` | No | Default `static/processed` |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase `anon` (public) key |
| `NEXT_PUBLIC_API_URL` | Yes | Your FastAPI backend URL |

---

## Project Structure

```
pinforge-ai/
│
├── backend/                        FastAPI backend (Railway)
│   ├── main.py                     App entry point + CORS + lifespan
│   ├── config.py                   All settings via env vars, safety caps
│   ├── database.py                 SQLAlchemy engine + session management
│   ├── models.py                   ORM models: User, PinterestAccount, PinQueue, PostHistory
│   ├── middleware/
│   │   └── auth.py                 Supabase JWT verification → User lookup
│   ├── routers/
│   │   ├── accounts.py             Pinterest OAuth connect/disconnect/boards
│   │   ├── pins.py                 Image upload, AI generation, queue CRUD
│   │   ├── analytics.py            Overview stats + daily chart data
│   │   └── settings_router.py      User profile + AI key management
│   ├── services/
│   │   ├── pinterest_service.py    Official Pinterest API v5 wrapper
│   │   ├── ai_service.py           Multi-provider AI: Gemini, OpenAI, DeepSeek
│   │   ├── image_service.py        Pillow: 2:3 crop, EXIF strip, JPEG optimize
│   │   └── scheduler_service.py    APScheduler: safety checks + posting
│   ├── requirements.txt
│   ├── Procfile                    Railway start command
│   └── .env.example
│
└── frontend/                       Next.js 14 frontend (Vercel)
    ├── app/
    │   ├── layout.tsx              Root layout + Toaster
    │   ├── globals.css             Tailwind base + custom components
    │   ├── page.tsx                Landing page (hero, features, pricing)
    │   ├── auth/
    │   │   ├── login/page.tsx      Login with Supabase auth
    │   │   └── signup/page.tsx     Signup with Supabase auth
    │   └── dashboard/
    │       ├── layout.tsx          Auth guard + sidebar shell
    │       ├── page.tsx            Overview: stats + chart + quick actions
    │       ├── create/page.tsx     Image upload + AI generation + queue
    │       ├── queue/page.tsx      Queue management: filter, remove, status
    │       ├── analytics/page.tsx  Charts + history log
    │       ├── accounts/page.tsx   Pinterest account connect/disconnect
    │       └── settings/page.tsx   Profile + AI keys + safety info
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.tsx         Navigation sidebar with active state
    │   │   └── Header.tsx          Page header + user avatar
    │   └── ui/
    │       └── StatsCard.tsx       Animated metric card
    ├── lib/
    │   ├── supabase.ts             Supabase browser client
    │   ├── api.ts                  Axios client + all API calls
    │   └── utils.ts                cn(), formatDate(), statusColor()
    ├── types/index.ts              TypeScript interfaces
    ├── package.json
    ├── tailwind.config.ts          Custom design tokens + animations
    ├── tsconfig.json
    └── .env.local.example
```

---

## Phase 2 Roadmap

Phase 2 turns PinForge AI into a full commercial SaaS product:

| Feature | Description |
|---------|-------------|
| 💳 **Stripe subscriptions** | Free / Pro ($19/mo) / Agency ($49/mo) plans with enforced limits |
| 📊 **Pinterest analytics** | Real impressions, saves, clicks via Pinterest API |
| 🤖 **AI image generation** | Generate pin images with DALL-E or Gemini Imagen |
| 👥 **Team accounts** | Invite team members, role-based access (owner / editor / viewer) |
| 🔔 **Notifications** | Email/Webhook alerts when pins post or fail |
| 📅 **Calendar view** | Visual drag-and-drop scheduling calendar |
| 🏷️ **Bulk board management** | Assign different images to different boards in one upload |
| 🌐 **White-label** | Custom domains for agency clients |
| 📱 **Mobile app** | React Native companion app |
| 🔌 **Zapier integration** | Trigger pin creation from external tools |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit with conventional commits: `git commit -m "feat: add xyz"`
4. Push and open a Pull Request

Please follow the existing code style and add comments for non-obvious logic.

---

## License

MIT © 2024 PinForge AI

---

<div align="center">

**Built with 📌 for creators who pin smarter.**

[⬆ Back to top](#pinforge-ai)

</div>
