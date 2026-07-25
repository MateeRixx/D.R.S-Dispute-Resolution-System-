from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.disputes import router as disputes_router
from app.api.users import router as users_router
from app.api.merchants import router as merchants_router
from app.api.evidence import router as evidence_router
from app.api.portal import router as portal_router

app = FastAPI(
    title="DRS — Dispute Resolution System",
    version="1.0.0",
    description="AI-powered dispute resolution platform for e-commerce chargebacks.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(disputes_router)
app.include_router(users_router)
app.include_router(merchants_router)
app.include_router(evidence_router)
app.include_router(portal_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
