# DRS — Dispute Resolution System

AI-powered chargeback resolution platform for Indian D2C e-commerce. Automates evidence gathering, OCR/vision analysis, deterministic scoring, and LLM-generated verdicts.

---

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.13+, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| AI/OCR | Gemini 2.0 Flash (vision + OCR), Claude 3.5 Sonnet (reasoning) |
| Frontend | React 19, Vite 8, GSAP 3, Three.js, Tailwind CSS |
| Auth | JWT (PyJWT), RBAC (customer / merchant / admin) |
| Integrations | Razorpay, Shopify, Shiprocket |

---

## Current State

### ✅ Completed

**Phase 1 — Database + Core API**
- PostgreSQL models: User, Dispute, Evidence, AuditTrail, MerchantDispute, DisputeLog
- CRUD endpoints: disputes, evidence, merchants, users
- Alembic migrations configured
- 7 tests passing

**Phase 2 — OCR + Vision**
- Gemini 2.0 Flash for document OCR and image analysis
- Evidence upload endpoint with structured extraction prompts
- 10 tests passing

**Phase 3 — Auto-Fetch + Adjudication**
- Razorpay/Shopify/Shiprocket async fetchers with BackgroundTasks
- 5-rule deterministic scoring matrix (documentation, timeline, evidence quality, merchant cooperation, amount ratio)
- 11 tests passing

**Phase 4 — Reasoning Engine**
- Prompt pipeline: evidence summary → fairness scores → PII-scrubbed narrative → merchant policy → reason code → amount
- Primary: Claude 3.5 Sonnet → Fallback: Gemini 2.0 Flash → Fallback: deterministic verdict
- PII scrubbing: cards, phones, emails via `security.py`
- Adjudication service calls `generate_verdict()`, sets verdict/confidence/status, writes audit trail
- 24 new tests (security 7, reasoning 11, portal 5, adjudication 1)

**Phase 4 — Frontend**
- Landing page: full-viewport hero, 3D HeroScene (Three.js), 400-particle system, magnetic buttons, card tilt, marquee strip, custom cursor, GSAP scroll-triggered animations, Lenis-free smooth native scroll
- Portal pages: CustomerPortal (dispute list + create + detail with stepper/verdict/evidence), MerchantDashboard (stats + defence upload), AdminAuditLog (expandable audit trail)
- Reusable components: Navbar, PortalLayout, DisputeStepper, VerdictCard, EvidenceInspector, UploadZone, LoginModal, CardTilt, CustomCursor, MagneticButton, MarqueeStrip, HeroScene
- SSE hook (`useDisputeSSE`) for live dispute updates
- API client library (`lib/api.js`)
- Design tokens in Tailwind config (warm ivory + deep navy palette)

**Testing**
- 51 backend tests passing (pytest-asyncio, transaction-per-test isolation, NullPool)
- conftest: fixed asyncpg connection reuse, removed deprecated `event_loop` fixture

---

## Execution Plan — Phases 5–8

### Phase 5 — Frontend–Backend Integration (Next)

Wire every frontend page to real backend APIs.

**5.1 — Auth Flow**
- LoginModal → `POST /api/auth/login` → receive JWT → store in memory/localStorage
- `lib/api.js` — attach `Authorization: Bearer <token>` header, handle 401 → redirect to login
- `Navbar` — show user name + logout when authenticated, role-based nav items

**5.2 — Customer Portal**
- Dispute list: `GET /portal/disputes` with user/status filters → render in table/grid
- Create dispute: form → `POST /api/disputes`
- Detail view: `GET /portal/disputes/{id}` → populate stepper, verdict card, evidence inspector
- SSE: connect to `GET /portal/disputes/{id}/events` → update stepper/status in real time
- Evidence upload: `POST /api/disputes/{id}/evidence`

**5.3 — Merchant Dashboard**
- Stats: aggregate calls or dedicated `GET /merchant/stats` → stats cards
- Dispute list: `GET /merchant/disputes` → dispute table
- Defence upload: evidence upload form for merchant-side documents

**5.4 — Admin Audit Log**
- `GET /admin/audit` → paginated list of AuditTrail entries with expandable metadata

**Verification:** User can log in as customer, file a dispute, see it progress to verdict via SSE.

### Phase 6 — Error Handling + Loading States

**6.1 — Unified error boundary** — React error boundary wrapping each page, with retry
**6.2 — Loading skeletons** — skeleton placeholders for dispute list, detail, audit log
**6.3 — Toast notifications** — success/error toasts for create/upload actions
**6.4 — Offline/retry** — SSE reconnect logic, retry on API failure with exponential backoff
**6.5 — Form validation** — client-side validation for dispute creation, evidence upload

**Verification:** Kill backend while using app → see graceful error states → restart → app recovers.

### Phase 7 — Production Readiness

**7.1 — Docker**
- `Dockerfile` (backend): Python 3.13 slim, uvicorn
- `Dockerfile` (frontend): Nginx serving static build
- `docker-compose.yml`: postgres + backend + frontend, env vars, volumes

**7.2 — CI/CD**
- GitHub Actions: lint → test → build → docker push (or deploy)
- Backend: `ruff check`, `pytest`
- Frontend: `eslint`, `vite build`

**7.3 — Security hardening**
- Rate limiting on auth endpoint
- CORS tightened to production domain
- Helmet-style headers via middleware

**Verification:** `docker compose up --build` → app accessible on `localhost:80` → full flow works.

### Phase 8 — Feature Enhancements

**8.1 — Dashboard analytics**
- Charts (dispute volume, resolution rate, avg time, merchant breakdown)
- Date range picker + export CSV

**8.2 — Email notifications**
- SendGrid / SMTP integration for dispute status changes
- Email templates for verdict, evidence request, escalation

**8.3 — Bulk operations (admin)**
- Select multiple disputes → bulk assign, re-adjudicate, export
- CSV/Excel import for existing disputes

**8.4 — Webhook endpoint**
- External systems can push dispute events
- Webhook signing + retry logic

**8.5 — Mobile responsive pass**
- Audit all portal/merchant/admin pages for mobile breakpoints
- Touch-friendly interactions (swipe, long-press)

**Verification:** All 8.1–8.5 features functional, tests passing, no regression.

---

## Quick Start

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Ensure PostgreSQL is running, then:
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npx vite
```

Backend at `http://localhost:8000`, frontend at `http://localhost:5173`.

---

## Project Structure

```
DRS/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route modules
│   │   ├── core/           # Config, DB, security
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic (OCR, reasoning, adjudication, auto-fetch)
│   │   └── main.py         # FastAPI app entry
│   ├── alembic/            # DB migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── hooks/          # Custom React hooks (SSE)
│   │   ├── lib/            # API client
│   │   ├── pages/          # Route pages
│   │   ├── App.jsx         # Router
│   │   └── main.jsx        # Entry
│   └── tailwind.config.js
├── .env                    # Environment variables (gitignored)
└── README.md
```
