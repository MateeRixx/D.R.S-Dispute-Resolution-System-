from fastapi import FastAPI

from app.api.disputes import router as disputes_router
from app.api.users import router as users_router
from app.api.merchants import router as merchants_router

app = FastAPI(
    title="DRS — Dispute Resolution System",
    version="0.1.0",
    description="AI-powered dispute resolution platform for e-commerce chargebacks.",
)

app.include_router(disputes_router)
app.include_router(users_router)
app.include_router(merchants_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
