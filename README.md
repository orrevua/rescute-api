# Rescute API 🐾

Backend for **Rescute** — a cat adoption and donation platform that connects independent cat protectors (NGOs, shelters, rescuers) with adopters, foster homes, and donors. Includes an AI-powered cat-care Q&A assistant.

- **Live API (Swagger docs):** https://rescute-api.onrender.com/docs (free Render tier — may cold-start for ~1 minute)
- **Live app:** https://rescute.vercel.app
- **Frontend repository:** [orrevua/rescute](https://github.com/orrevua/rescute) (Next.js)
- **Stack:** Python 3.12 · FastAPI · SQLAlchemy 2 (async) · PostgreSQL · Alembic · JWT auth · OpenAI-compatible AI provider
- **Architecture:** Hexagonal (ports & adapters) — `app/domain` (entities/ports) → `app/application` (services) → `app/adapters` (inbound API routers, outbound persistence/AI)

> All UI text in the product is Brazilian Portuguese (pt-BR); all code and documentation are in English.

## Features (API surface)

| Area | Endpoints | Auth |
|---|---|---|
| Auth | register, login, refresh, logout (server-side token revocation) | public / bearer |
| Cats | list/search cats, cat details, protector CRUD | public read, protector write |
| Adoption | adoption applications | authenticated |
| Foster | foster ("lar temporário") applications | authenticated |
| Donations | donation posts + public pledge contributions | public read/pledge, protector write |
| AI Care | cat-care Q&A chat (`/ai-care`) | public, rate-limited |
| Partners | partner clinics/stores with discounts | public read, protector write |
| Dashboard | protector metrics | protector |
| Uploads | image upload with magic-byte validation (jpeg/png/webp) | protector |

Security hardening included: typed JWTs (access/refresh) with version-based revocation, rate limiting (slowapi), security headers + CSP, strict CORS, upload content sniffing, generic client errors with server-side logging, `pip-audit` CI gate.

## Requirements

- Python 3.12+
- PostgreSQL 16 (or Docker)
- An OpenAI-compatible API key (optional — only needed for the AI care chat)

## Local setup

```bash
# 1. Clone
git clone https://github.com/orrevua/rescute-api.git
cd rescute-api

# 2. Virtual env + dependencies
python -m venv venv
# Windows: venv\Scripts\activate    |    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# 3. Database (Docker, from repo root)
docker run -d --name rescute-db -p 5432:5432 \
  -e POSTGRES_DB=rescute -e POSTGRES_USER=rescute -e POSTGRES_PASSWORD=rescute \
  postgres:16-alpine

# 4. Environment
cp .env.example .env
# Set SECRET_KEY (required, >= 32 chars):
#   python -c "import secrets; print(secrets.token_urlsafe(48))"
# Optionally set AI_PROVIDER_KEY for the AI chat.

# 5. Migrations + seed data
alembic upgrade head
python -m scripts.seed

# 6. Run
uvicorn app.main:app --reload --port 8000
```

API docs (Swagger): http://127.0.0.1:8000/docs

## Environment variables

See [.env.example](.env.example). Summary:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | yes | `postgresql+asyncpg://rescute:rescute@localhost:5432/rescute` |
| `SECRET_KEY` | yes | JWT signing key, ≥ 32 chars — the app refuses to boot without it |
| `ENVIRONMENT` | no | `production` drops localhost CORS origins (default `development`) |
| `AI_PROVIDER_KEY` | no | OpenAI-compatible key for the AI care chat |
| `AI_MODEL` / `AI_BASE_URL` | no | Defaults: `gpt-4o-mini` / `https://api.openai.com/v1` |
| `FRONTEND_URL` | no | Deployed frontend origin allowed by CORS |

## Test credentials (seeded)

`python -m scripts.seed` creates a protector account with one cat, one partner clinic, and one donation post:

- **Email:** `protetor@rescute.app`
- **Password:** `Rescute123!`

## Deployment

Deployed on [Render](https://render.com) via `render.yaml` (build runs `pip install` + `alembic upgrade head`, serves with uvicorn). Database on Neon (managed Postgres). CI (`.github/workflows/security-audit.yml`) runs `pip-audit` on every push/PR to `main`.

## Project layout

```
app/
  domain/        # entities + repository ports (pure, framework-free)
  application/   # use-case services (auth, cats, donations, AI care, ...)
  adapters/
    inbound/api/   # FastAPI routers, schemas, auth middleware
    outbound/      # SQLAlchemy persistence, AI provider client
  main.py        # app wiring: CORS, rate limiter, security headers
alembic/         # migrations (001–004)
scripts/seed.py  # development/demo seed data
```
