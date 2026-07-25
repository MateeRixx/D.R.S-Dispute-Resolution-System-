# AI-Powered ODR System — Master Blueprint

> Automated Online Dispute Resolution for Indian D2C E-commerce Credit Card Transactions

---

## What This Is

A zero-bias, AI-powered dispute resolution platform that automatically gathers transaction, order, and shipping evidence; processes visual/textual proof via Multimodal Vision AI; applies deterministic weighing algorithms; and generates human-readable adjudication verdicts.

---

## Document Index

| # | File | Contents |
|---|------|----------|
| 1 | [`01-PRD.md`](./01-PRD.md) | Product requirements, personas, functional specs |
| 2 | [`02-DATABASE.md`](./02-DATABASE.md) | PostgreSQL schema, ERD, DDL, concurrency rules |
| 3 | [`03-ARCHITECTURE.md`](./03-ARCHITECTURE.md) | Tech stack, directory layout, UI/UX guidelines |
| 4 | [`04-SECURITY.md`](./04-SECURITY.md) | PCI-DSS, RBAC, API/webhook security, encryption |
| 5 | [`05-IMPLEMENTATION.md`](./05-IMPLEMENTATION.md) | Phase-wise build plan, verification gates, testing |

---

## System Flow

```
[ Disputed Transaction Triggered ]
              │
 ┌────────────┴────────────┐
 ▼                         ▼
[ Auto-Gathering API ]  [ Manual Evidence Upload ]
  Razorpay / Shopify /    Receipt Photos /
  Shiprocket              Chat Screenshots
 │                         │
 └────────────┬────────────┘
              ▼
  [ Ingestion & OCR Pipeline ]
       (Gemini 1.5 Flash)
              ▼
   [ Fair-Weighing Logic Engine ]
     (Rule Matrix + Point Scoring)
              ▼
   [ Reasoned Decision Synthesis ]
        (Claude 3.5 Sonnet)
              ▼
[ Real-Time Audit & Verdict Dashboard ]
```

---

## Quick Start for AI Agents / Engineers

1. **Read all 5 documents** in order before writing any code.
2. **Implement Phase 1** (`01-PRD.md` → `05-IMPLEMENTATION.md` Phase 1) completely.
3. **Pass verification gates** before advancing to the next phase.
4. **Obtain user validation** at the end of each phase.

---

## Verdict Output Shape

```json
{
  "verdict": "REFUND_USER | REJECT_CLAIM | PARTIAL_REFUND | NEEDS_HUMAN_INTERVENTION",
  "confidence_score": 0.0,
  "reasoning_summary": "Plain-language explanation of the decision"
}
```
