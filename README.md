<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=13&duration=2000&pause=500&color=A78BFA&center=true&vCenter=true&multiline=true&repeat=false&width=700&height=80&lines=Initializing+dispute+resolution+pipeline...;Evidence+gathered.+Scoring+complete.+Verdict+rendered+in+28s." alt="Typing SVG" />
</p>

<br/>

```
 ██████╗     ██████╗      ███████╗
 ██╔══██╗    ██╔══██╗     ██╔════╝
 ██║  ██║    ██████╔╝     ███████╗
 ██║  ██║    ██╔══██╗     ╚════██║
 ██████╔╝    ██║  ██║     ███████║
 ╚═════╝     ╚═╝  ╚═╝     ╚══════╝

          DISPUTE  RESOLUTION  SYSTEM
    AI-powered chargeback verdicts in < 30s
```

<p align="center">
  <img src="https://img.shields.io/badge/verdict_speed-28_seconds-a78bfa?style=flat-square&labelColor=0d1117"/>
  <img src="https://img.shields.io/badge/manual_cost_eliminated-₹1.5L%2Fmonth-34d399?style=flat-square&labelColor=0d1117"/>
  <img src="https://img.shields.io/badge/evidence_sources-3_parallel_APIs-f472b6?style=flat-square&labelColor=0d1117"/>
  <img src="https://img.shields.io/badge/LLM_fallback_chain-Groq_→_Gemini_→_deterministic-fb923c?style=flat-square&labelColor=0d1117"/>
</p>

---

> *A chargeback lands. Razorpay pinged. Shopify queried. Shiprocket checked.
> Gemini reads the invoice. The defect is real. Score: User 25, Merchant 10.
> Groq writes the verdict. The customer is refunded.*
>
> **Time elapsed: 28 seconds.** No human touched it.

---

## The Problem Nobody Talks About

Every D2C founder obsesses over CAC and LTV. Nobody talks about the 3pm Slack message: *"We have 47 open chargebacks."*

Someone opens Razorpay. Someone else opens Shopify. A third person DMed the logistics team. Two hours later, half are resolved with inconsistent decisions, no documentation, and a spreadsheet nobody will update.

**DRS kills that workflow entirely.**

---

## What Actually Happens When a Dispute Comes In

```
Customer clicks "I didn't receive this"
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 1 — INTAKE                                   │
│  POST /disputes/  →  dispute created, ID assigned   │
│  Background pipeline fires immediately              │
└────────────────────┬────────────────────────────────┘
                     │  ~100ms
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 2 — EVIDENCE GATHERING  (parallel)           │
│                                                     │
│  asyncio.gather(                                    │
│    razorpay.get_transaction(txn_id),    ← CAPTURED? │
│    shopify.get_order(order_id),         ← FULFILLED?│
│    shiprocket.get_delivery(awb),        ← SIGNED?   │
│  )                                                  │
│                                                     │
│  Status → EVIDENCE_GATHERING                        │
│  SSE pushes update to customer's browser            │
└────────────────────┬────────────────────────────────┘
                     │  ~800ms
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 3 — AI VISION (if evidence uploaded)         │
│                                                     │
│  Gemini 2.0 Flash reads the invoice image           │
│  → Extracts: vendor, line items, total amount       │
│                                                     │
│  Gemini 2.0 Flash inspects the product photo        │
│  → Returns: defects[], confidence, bounding_boxes   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 4 — SCORING                                  │
│                                                     │
│  Rule                      │ Points │ Side          │
│  ──────────────────────────┼────────┼──────────     │
│  shiprocket_delivered      │  +10   │ Merchant      │
│  shiprocket_signature      │  +15   │ Merchant      │
│  defects_detected          │  +15   │ User          │
│  refund_policy_violated    │  +10   │ User          │
│  razorpay_failed           │  +20   │ User          │
│                                                     │
│  Max possible: Merchant 25 pts  /  User 45 pts      │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 5 — REASONING                                │
│                                                     │
│  Groq LLaMA 3 70B  ──✗──▶  Gemini 2.0 Flash        │
│         PRIMARY    fails       FALLBACK 1           │
│                                    │                │
│                               ──✗──▶  Deterministic │
│                               fails    FALLBACK 2   │
│                                       (always wins) │
│                                                     │
│  PII scrubbed before any token leaves your server   │
│  diff ≥ 15  →  hard verdict                         │
│  diff > 0   →  PARTIAL_REFUND + %                   │
│  diff = 0   →  NEEDS_HUMAN_INTERVENTION             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 6 — VERDICT                                  │
│                                                     │
│  Persisted to DB with confidence score              │
│  SSE pushes live to customer browser                │
│  Email sent via Resend API                          │
│  Audit trail entry written (tamper-evident)         │
└─────────────────────────────────────────────────────┘
```

---

## Four Verdicts. No Ambiguity.

| Verdict | When it fires |
|:---|:---|
| `REFUND_USER` | Evidence clearly favors the customer. Done. |
| `REJECT_CLAIM` | Delivery confirmed, signature present, payment clean. |
| `PARTIAL_REFUND` | Mixed signals — system calculates a fair percentage. |
| `NEEDS_HUMAN_INTERVENTION` | Genuinely ambiguous. Routed to a human with full context pre-loaded. |

---

## Five Reason Codes. Every Chargeback Covered.

```
ITEM_NOT_RECEIVED        →  cross-checked against Shiprocket delivery + GPS scan
ITEM_DEFECTIVE           →  Gemini Vision detects defects from photo evidence
INCORRECT_AMOUNT         →  Razorpay amount diff'd against Shopify order total
UNAUTHORIZED_TRANSACTION →  fraud flags, device fingerprint, IP match analysis
SUBSCRIPTION_CANCELLED   →  billing date vs cancellation timestamp logic
```

---

## The Stack, Without the Fluff

```
Backend        FastAPI + SQLAlchemy 2.0 + asyncpg → Python 3.13
Database       PostgreSQL 16
AI Vision      Gemini 2.0 Flash       (OCR + defect detection)
AI Reasoning   Groq LLaMA 3 70B       (primary verdict writer)
               Gemini 2.0 Flash       (fallback 1)
               Deterministic engine   (fallback 2 — always resolves)
Frontend       React 19 + Vite 8 + Three.js + GSAP + Tailwind
Auth           JWT + RBAC             (customer / merchant / admin)
Realtime       Server-Sent Events     (live verdict delivery)
Integrations   Razorpay · Shopify · Shiprocket
Email          Resend API
Infra          Docker + docker-compose + GitHub Actions CI
```

---

## Database, Actually Explained

Five tables that matter:

**`disputes`** — The core record. Owns the `reason_code` (5 types), `status` (5 states: `INITIATED → EVIDENCE_GATHERING → UNDER_REVIEW → DECISION_RENDERED → CLOSED`), `verdict`, and `confidence_score`.

**`evidence`** — Every uploaded file. Stores Gemini's raw OCR JSON and Vision JSON as JSONB. `uploaded_by` can be `USER`, `MERCHANT`, or `AUTO_API`.

**`auto_fetched_logs`** — One row per dispute. Three JSONB columns: the raw Razorpay payload, Shopify payload, Shiprocket payload — exactly as returned.

**`audit_trail`** — Append-only. Every state transition, every upload, every verdict — logged with actor ID or `SYSTEM_AGENT` and a metadata blob.

**`merchants`** — Holds the Shopify domain, hashed API keys, and return policy URL used to evaluate `refund_policy_violated`.

---

## API Surface

```
POST   /disputes/                      Create dispute → triggers pipeline
GET    /disputes/{id}                  Full dispute + all relations
GET    /portal/disputes                List (filterable by status/user/merchant)
GET    /portal/disputes/{id}/events    SSE stream → live updates to browser
POST   /evidence/upload                Multipart → Gemini OCR + Vision
POST   /auth/login                     JWT issuance
GET    /admin/stats                    Verdict distribution, volume, trends
POST   /admin/bulk/re-adjudicate       Re-run AI pipeline on N disputes
POST   /admin/bulk/export              CSV dump
POST   /webhooks/dispute-event         HMAC-signed external event ingestion
```

---

## Frontend: Four Views, One System

```
/                   Landing          3D particle scene (Three.js) · GSAP hero
/portal             Customer         File dispute · upload evidence · live SSE verdict
/merchant           Merchant         Stats · case list · defence upload
/admin              Audit Log        Every system action, expandable, timestamped
/admin/analytics    Analytics        Charts · date range · one-click CSV
```

The SSE hook (`useDisputeSSE`) auto-reconnects up to 10 times with exponential backoff. The API client retries failed requests 3× before surfacing an error. Nothing silently fails.

---

## Run It

**With Docker (30 seconds)**

```bash
git clone https://github.com/MateeRixx/D.R.S-Dispute-Resolution-System-
cd D.R.S-Dispute-Resolution-System-
docker-compose up --build
```

**Without Docker**

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env          # fill in API keys
python -m alembic upgrade head
python app/seed.py
uvicorn app.main:app --reload  # → localhost:8000

# Frontend
cd frontend
npm install
npx vite                       # → localhost:5173
```

**Demo logins**

```
alice@example.com    →  customer   (file disputes, track verdicts)
merchant@acme.com    →  merchant   (view cases, submit defence)
admin@drs.com        →  admin      (everything + bulk ops + analytics)

password: password
```

---

## Testing

```bash
pytest tests/ -v                     # full suite
pytest tests/evaluation/ --fast      # deterministic eval only (no LLM calls)
pytest tests/evaluation/             # full LLM eval against golden dataset
```

40 hand-labeled golden test cases across all 5 reason codes × all 4 verdicts. Scenarios include: empty user narratives, missing merchant policies, partial deliveries, duplicate charges, paused subscriptions, currency mismatches, and cases where evidence genuinely favors neither side.

**Deterministic accuracy: 18/40 (45%)** — the rest are handled by the LLM pipeline.

---

## Security

- JWT on every authenticated route; roles enforced at handler level
- PII scrubber strips card numbers, phone numbers, email addresses before any LLM call
- Webhooks verified with HMAC-SHA256 — unsigned payloads rejected
- Rate limiting per IP on all public endpoints
- CORS locked to configured origin allowlist

---

## Project Layout

```
DRS/
├── backend/
│   ├── app/
│   │   ├── api/            route handlers
│   │   ├── core/           config, DB, security, rate limiting
│   │   ├── models/         SQLAlchemy ORM
│   │   ├── schemas/        Pydantic in/out
│   │   └── services/
│   │       ├── auto_fetch.py       parallel API calls
│   │       ├── ocr_vision.py       Gemini OCR + Vision
│   │       ├── reasoning.py        LLM pipeline + PII scrub
│   │       ├── adjudication.py     5-rule scoring
│   │       └── email_service.py    Resend templates
│   ├── alembic/
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── components/     Navbar · VerdictCard · UploadZone · EvidenceInspector
│       ├── hooks/          useDisputeSSE
│       ├── lib/            api.js — JWT, retry, SSE reconnect
│       └── pages/          Landing · Portal · Merchant · Admin · Analytics
│
├── Test/                   40-case golden dataset
└── docker-compose.yml
```

---

<p align="center">
  <sub>Built for Indian D2C · Razorpay · Shopify · Shiprocket · Made with the conviction that no human should spend 20 minutes on a chargeback</sub>
</p>

<p align="center">
  <a href="https://github.com/MateeRixx/D.R.S-Dispute-Resolution-System-">⭐ Star this if it sparked something</a>
</p>
