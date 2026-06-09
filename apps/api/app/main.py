from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.v1.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    register_error_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
