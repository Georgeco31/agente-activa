from fastapi import APIRouter

from app.api.v1 import agent, customers, dashboard, health, orders, products

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(agent.router)
api_router.include_router(customers.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(dashboard.router)
