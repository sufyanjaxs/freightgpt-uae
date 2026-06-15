from fastapi import APIRouter
from api.v1 import auth, users, loads, fleet, agents, documents, finance, communications, analytics, webhooks

v1_router = APIRouter()

v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(users.router, prefix="/users", tags=["Users"])
v1_router.include_router(loads.router, prefix="/loads", tags=["Loads"])
v1_router.include_router(fleet.router, prefix="/fleet", tags=["Fleet"])
v1_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
v1_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
v1_router.include_router(finance.router, prefix="/finance", tags=["Finance"])
v1_router.include_router(communications.router, prefix="/communications", tags=["Communications"])
v1_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
