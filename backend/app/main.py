from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.disputes import router as disputes_router
from app.api.users import router as users_router
from app.api.merchants import router as merchants_router
from app.api.evidence import router as evidence_router
from app.api.portal import router as portal_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router

app = FastAPI(
    title="DRS — Dispute Resolution System",
    version="1.0.0",
    description="AI-powered dispute resolution platform for e-commerce chargebacks.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(disputes_router)
app.include_router(users_router)
app.include_router(merchants_router)
app.include_router(evidence_router)
app.include_router(portal_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
