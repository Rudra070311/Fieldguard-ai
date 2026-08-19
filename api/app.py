from __future__ import annotations
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from config.settings import Settings
from api.middleware import setup_middleware
from api.router import api_router

def configure_logging(settings: Settings) -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, settings.logging.level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    return logging.getLogger("ideez")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = app.state.logger
    logger.info("iDeez API starting")
    yield
    logger.info("iDeez API shutting down")

def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    logger = configure_logging(settings)
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.logger = logger

    setup_middleware(
        app=app,
        settings=settings,
    )

    app.include_router(api_router)

    @app.get(
        "/health",
        tags=["system"],
    )
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.app.name,
            "version": settings.app.version,
        }

    return app

app = create_app()

__all__ = [
    "app",
    "create_app",
]