# Project Pilot — AI Project Generator SaaS

Project Pilot is an AI-powered SaaS platform that helps students generate complete
academic projects — reports, presentations, and source code — in minutes. It ships
with a multi-tenant backend (organizations, teams, SSO), Stripe billing, an
in-browser code editor, and a premium Apple-inspired UI.

## 🚀 Features

- **AI Project Generation** — abstract, architecture, and full source code via a multi-provider LLM client (Groq / Gemini / OpenAI / Anthropic).
- **In-browser Code Editor** — Monaco editor with file tree, sandboxed code execution (Docker), live preview, and an AI "improve this code" assistant.
- **Viva Assistant** — AI mock interviewer to prepare for project defense.
- **Document Generation** — industry-standard PDF reports and PPTX presentations.
- **Multi-tenant SaaS** — organizations, teams & collaboration, role-based access, org branding, SSO/SAML.
- **Billing** — Stripe subscriptions, invoicing, usage metering, tiered plans.
- **Async processing** — Celery + Redis for long-running generation jobs, with websocket progress updates.

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, Shadcn UI, Framer Motion |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Data | PostgreSQL (prod) / SQLite (dev), Redis |
| Async | Celery workers |
| AI | Multi-provider via litellm |
| Billing | Stripe |
| Observability | Structured logging, request-id correlation, optional Sentry |

## 📦 Project Structure

```
├── frontend/              # Next.js frontend (deploys to Vercel)
│   ├── app/               # App Router pages
│   ├── components/        # Reusable UI components
│   └── services/api.ts    # Centralized API client
├── backend/               # FastAPI backend (deploys to Render/Railway)
│   ├── app/
│   │   ├── api/           # Route handlers (v1/ is the current API surface)
│   │   ├── core/          # config.py (settings), observability.py, generators
│   │   ├── models/        # SQLAlchemy models (registered in models/__init__.py)
│   │   ├── services/      # Business logic (sandbox, stripe, projects)
│   │   └── main.py        # App entry point
│   ├── alembic/           # Database migrations (source of truth in prod)
│   ├── scripts/           # Operational scripts (create_admin, reset_password)
│   ├── tests/             # pytest suite
│   └── Dockerfile
├── render.yaml            # Render blueprint (API + worker + Redis + Postgres)
└── .github/workflows/     # CI (backend pytest, frontend typecheck + build)
```

## ⚡ Local Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker (optional — required only for sandboxed code execution)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env              # then fill in values
uvicorn app.main:app --reload     # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local        # then set NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev                        # http://localhost:3000
```

### Optional: full stack via Docker Compose (Postgres + Redis + API + worker)
```bash
cd backend
docker compose up --build
```

## 🧪 Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

CI runs the backend test suite and a frontend typecheck + production build on every
push and pull request (see `.github/workflows/ci.yml`).

## 🔑 Environment Variables

Both services use their own `.env.example` as the canonical reference:

- **Backend** — `backend/.env.example` (core, database, Redis/Celery, AI provider, Stripe, SMTP, SSO, observability). Config is validated at startup; in production the app refuses to boot with a weak `SECRET_KEY`, a SQLite `DATABASE_URL`, or missing `ALLOWED_ORIGINS`.
- **Frontend** — `frontend/.env.example` (`NEXT_PUBLIC_API_URL` etc.).

Generate a secret key with: `python -c "import secrets; print(secrets.token_hex(32))"`

## ☁️ Deployment (Vercel + Render/Railway)

**Frontend → Vercel**
1. Import the repo in Vercel, set the root directory to `frontend/`.
2. Set `NEXT_PUBLIC_API_URL` to your backend URL + `/api` (e.g. `https://api.example.com/api`).
3. Deploy — Vercel auto-detects Next.js.

**Backend → Render** (blueprint provided)
1. In Render → **New +** → **Blueprint**, point it at this repo's `render.yaml`.
   It provisions the API, a Celery worker, Redis, and Postgres.
2. Fill the secret env vars marked `sync: false` (AI keys, Stripe keys, `ALLOWED_ORIGINS`, SMTP).
3. Migrations run automatically before each deploy (`alembic upgrade head`); the
   health check hits `/ready` (verifies DB connectivity).

**Backend → Railway** (alternative)
- Create a service from `backend/Dockerfile`, add Postgres and Redis plugins, and
  set the same env vars. Add a deploy/release command of `alembic upgrade head`.

### Health probes
- `GET /health` — liveness (process up).
- `GET /ready` — readiness (database reachable); returns 503 if the DB is down.

## 🗺️ Roadmap

- [x] AI project generation
- [x] Premium dashboard UI
- [x] Viva assistant
- [x] Stripe billing & invoicing
- [x] Teams & collaboration
- [x] In-browser code editor
- [ ] GitHub integration for direct pushing

## 📄 License

Proprietary — all rights reserved. See [LICENSE](LICENSE).
