from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.disputes import router as disputes_router
from app.api.evidence import router as evidence_router
from app.api.merchants import router as merchants_router
from app.api.portal import router as portal_router
from app.api.users import router as users_router
from app.api.webhooks import router as webhooks_router
from app.core.config import settings
from app.core.rate_limit import rate_limit_middleware

app = FastAPI(
    title="DRS — Dispute Resolution System",
    version="1.0.0",
    description="AI-powered dispute resolution platform for e-commerce chargebacks.",
)

origins = settings.cors_origins.split(",") if settings.cors_origins else ["http://localhost:5173", "http://localhost:80"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limit_middleware)

app.include_router(disputes_router)
app.include_router(users_router)
app.include_router(merchants_router)
app.include_router(evidence_router)
app.include_router(portal_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(webhooks_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
