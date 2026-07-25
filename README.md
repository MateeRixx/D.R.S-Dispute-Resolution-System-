# DRS — Dispute Resolution System

AI-powered chargeback resolution platform for Indian D2C e-commerce. Automates evidence gathering, OCR/vision analysis, deterministic scoring, and LLM-generated verdicts.

---

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.13+, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| AI/OCR | Gemini 2.0 Flash (vision + OCR), Groq (LLaMA 3 70B, reasoning) |
| Frontend | React 19, Vite 8, GSAP 3, Three.js, Tailwind CSS |
| Auth | JWT (PyJWT), RBAC (customer / merchant / admin) |
| Integrations | Razorpay, Shopify, Shiprocket |

---

## Features

### Phase 1 — Database + Core API
- PostgreSQL models: User, Merchant, Dispute, Evidence, AuditTrail, AutoFetchedLogs
- CRUD endpoints for disputes, evidence, merchants
- Alembic migrations with full schema history

### Phase 2 — OCR + Vision
- Gemini 2.0 Flash for document OCR and image analysis
- Evidence upload endpoint with structured extraction (invoice lines, defect regions)
- PII scrubbing before LLM processing

### Phase 3 — Auto-Fetch + Adjudication
- Razorpay / Shopify / Shiprocket data fetchers via BackgroundTasks
- 5-rule deterministic scoring matrix (documentation, timeline, evidence quality, merchant cooperation, amount ratio)
- 40-case golden dataset for correctness evaluation

### Phase 4 — Reasoning Engine + Frontend
- LLM pipeline: Groq (LLaMA 3 70B) → Gemini 2.0 Flash → deterministic fallback
- Evidence summary → fairness scores → PII-scrubbed narrative → merchant policy → verdict
- Landing page: full-viewport 3D HeroScene (Three.js), particle system, magnetic buttons, GSAP scroll animations
- Portal pages: CustomerPortal, MerchantDashboard, AdminAuditLog

### Phase 5 — Frontend–Backend Integration
- Login flow with JWT, role-based routing (customer/merchant/admin)
- Customer: file disputes, view live status via SSE, upload evidence
- Merchant: view assigned disputes, submit defence evidence
- Admin: full audit trail with expandable metadata

### Phase 6 — Error Handling
- ErrorBoundary, Toast notifications, loading skeletons
- SSE auto-reconnect with exponential backoff
- API retry with exponential backoff (3 retries)

### Phase 7 — Production Readiness
- Dockerfiles for backend (uvicorn) + frontend (Nginx)
- `docker-compose.yml` with Postgres + backend + frontend
- GitHub Actions CI: ruff lint → pytest → frontend lint → frontend build
- Rate limiting on `/auth/login`, configurable CORS

### Phase 8 — Feature Enhancements
- **8.1 Analytics:** Admin analytics page with stat cards, pie/bar charts, date-range filter, CSV export
- **8.2 Email:** Resend integration for dispute lifecycle notifications (created, evidence needed, verdict)
- **8.3 Bulk operations:** Admin bulk re-adjudicate and CSV export endpoints
- **8.4 Webhook:** HMAC-SHA256 signed webhook endpoint for external dispute events
- **8.5 Mobile responsive:** Bottom nav bar, responsive grid breakpoints, touch-friendly interactions

---

## Demo Credentials

| Role | Email |
|------|-------|
| Customer | `alice@example.com` |
| Merchant | `merchant@acme.com` |
| Admin | `admin@drs.com` |

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 16+

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Set up environment (copy from .env.example or create .env)
# Required: DATABASE_URL, JWT_SECRET_KEY, GEMINI_API_KEY, GROQ_API_KEY

# Run migrations
python -m alembic upgrade head

# Seed demo data
python app/seed.py

# Start server
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npx vite
```

### Access
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend UI: `http://localhost:5173`

---

## Evaluation

```bash
cd backend
# Dry-run (print scoring rules without LLM)
python tests/evaluate_correctness.py --dry-run

# Fast evaluation (deterministic only, ~30s)
python tests/evaluate_correctness.py --fast

# Full evaluation (with LLM, requires API keys, ~2-3 min)
python tests/evaluate_correctness.py
```

---

## Project Structure

```
DRS/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route modules (auth, disputes, portal, admin, webhooks, merchants, evidence)
│   │   ├── core/           # Config, DB, security, rate limiting
│   │   ├── models/         # SQLAlchemy ORM models (User, Merchant, Dispute, Evidence, AuditTrail, AutoFetchedLogs)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic (OCR/vision, reasoning, adjudication, auto-fetch, email)
│   │   └── main.py         # FastAPI app entry with CORS, middleware
│   ├── alembic/            # DB migrations
│   └── tests/              # Pytest test suite + golden dataset + evaluation harness
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI (Navbar, LoginModal, DisputeStepper, VerdictCard, etc.)
│   │   ├── hooks/          # Custom hooks (useDisputeSSE)
│   │   ├── lib/            # API client with retry logic
│   │   ├── pages/          # Route pages (Landing, CustomerPortal, MerchantDashboard, AdminAuditLog, AdminAnalytics)
│   │   ├── App.jsx         # Router with role guards
│   │   └── main.jsx        # Entry point
│   └── tailwind.config.js
├── Test/                   # Golden dataset (TestDataset.json)
├── docker-compose.yml      # Production container setup
└── README.md
```

---

## License

MIT
