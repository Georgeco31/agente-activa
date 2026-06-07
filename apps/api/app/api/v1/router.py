from fastapi import APIRouter

from app.api.v1 import customers, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(customers.router)
