#======================================#
#              main.py                 #
#======================================#

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.logging import get_logger
from app.config.database import engine
from app.config.settings import settings
from app.core.exception_handlers import register_exception_handlers
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.tenant_management.router import router as tenant_router
logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — school-ai-assistant API")
    yield
    logger.info("Shutting down — closing DB connections")
    await engine.dispose()


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="LearnlyAI Assistant",
        description="WhatsApp-powered school management assistant API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — tighten origins before going to production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(tenant_router, prefix="/api/v1/tenants", tags=["Tenants"])

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import logging
    import uvicorn

    from app.config.logging import is_development, resolve_log_level

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=is_development(),
        log_config=None,
        log_level=logging.getLevelName(resolve_log_level()).lower(),
    )
