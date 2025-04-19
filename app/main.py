import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as email_router
from app.core.config import settings
from app.dependencies import mongo_mgr, run_email_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Debug settings
logger.info("=" * 50)
logger.info("Starting application with settings:")
# logger.info(f"Loading settings from .env file: {settings.Config.env_file}")
logger.info(f"USER_EMAIL from settings: {settings.USER_EMAIL}")
logger.info(f"CLIENT_ID from settings: {settings.CLIENT_ID}")
logger.info(f"TENANT_ID from settings: {settings.TENANT_ID}")
logger.info("=" * 50)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Scheduler for periodic email retrieval
scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup():
    await mongo_mgr.ensure_database(settings.COLLECTIONS)
    scheduler.add_job(
        run_email_sync,
        "interval",
        minutes=settings.EMAIL_RETRIEVAL_INTERVAL_MINUTES,
    )
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    await mongo_mgr.close()
    scheduler.shutdown()


# Include routers
app.include_router(
    email_router,
    prefix=f"{settings.API_V1_STR}/emails",
    tags=["emails"],
)


@app.get("/")
async def root():
    return {"message": "Microsoft Graph API Email Service"}
