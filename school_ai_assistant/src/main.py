#==========================#
# MAIN SCRIPT
#==========================#

from fastapi import FastAPI

from .core.logging import setup_logging
from .routes.webhook import ai_service, router as webhook_router


setup_logging()

app = FastAPI()
app.include_router(webhook_router)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await ai_service.aclose()
