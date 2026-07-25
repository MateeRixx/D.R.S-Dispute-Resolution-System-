# DRS — Dispute Resolution System

## Project Description

An AI-powered chargeback resolution platform designed for Indian D2C e-commerce brands. The system automates the entire dispute lifecycle — from evidence gathering and OCR/vision analysis to deterministic scoring and LLM-generated verdicts — reducing resolution time from 15-30 minutes per case to under 30 seconds.

### Key Problems Solved
- **Manual evidence collection** across Razorpay (payments), Shopify (orders), and Shiprocket (logistics) — fully automated
- **Slow adjudication** — LLM pipeline generates reasoned verdicts in seconds
- **Inconsistent decisions** — deterministic scoring matrix + LLM reasoning ensures consistency
- **No audit trail** — every action logged with timestamps and metadata
- **No analytics** — admin dashboard with charts, date-range filtering, and CSV export

### Architecture
- **Frontend:** React 19 + Vite 8 with GSAP animations, Three.js 3D scenes, Tailwind CSS
- **Backend:** FastAPI with SQLAlchemy 2.0 + asyncpg, PostgreSQL 16
- **AI Pipeline:** Groq (LLaMA 3 70B) → Gemini 2.0 Flash → deterministic fallback
- **Infra:** Docker, docker-compose, GitHub Actions CI

### Features
- Auto-fetch from Razorpay, Shopify, and Shiprocket APIs
- OCR + Vision analysis via Gemini 2.0 Flash
- 5-rule deterministic scoring matrix
- LLM reasoning with PII scrubbing
- Real-time SSE updates to frontend
- Role-based portals: Customer, Merchant, Admin
- Email notifications via Resend
- Webhook API with HMAC-SHA256 signing
- Admin analytics with charts and CSV export
- Bulk re-adjudication and export
- Mobile responsive design
- Docker containerization
- CI/CD with GitHub Actions

## Setup Instructions

### Prerequisites
- Python 3.13+, Node.js 20+, PostgreSQL 16+

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Set DATABASE_URL, JWT_SECRET_KEY, GEMINI_API_KEY, GROQ_API_KEY in .env
python -m alembic upgrade head
python app/seed.py
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npx vite
```

### Access
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Demo Credentials
| Role | Email |
|------|-------|
| Customer | alice@example.com |
| Merchant | merchant@acme.com |
| Admin | admin@drs.com |

## Links
- **GitHub Repository:** https://github.com/MateeRixx/D.R.S-Dispute-Resolution-System-
- **Presentation:** See `Presentation.pptx` in the repository root
- **Video Demo:** (Link to be added)
