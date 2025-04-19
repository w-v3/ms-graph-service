from functools import lru_cache

from app.auth.ms_device_code_flow import DeviceCodeFlow
from app.core.config import settings
from app.db.connection.mongo import MongoConnectionManager
from app.db.mongo_email_repository import MongoEmailRepository
from app.mail.ms_graph_client import GraphMailClient
from app.services.email_manager import EmailManager

# 1. Core dependencies
mongo_mgr = MongoConnectionManager(settings.MONGO_URI, settings.DATABASE_NAME)
auth_flow = DeviceCodeFlow(settings.CLIENT_ID, settings.TENANT_ID, settings.SCOPES,settings.MS_GRAPH_AUTH_URL)


# 2. Factory functions
@lru_cache
def get_mail_client():
    return GraphMailClient(auth_flow, settings.USER_EMAIL,settings.MS_GRAPH_API_URL)


@lru_cache
def get_email_repo():
    return MongoEmailRepository(mongo_mgr)


@lru_cache
def get_email_manager():
    return EmailManager(
        mail_client=get_mail_client(),
        email_repo=get_email_repo(),
        user_email=settings.USER_EMAIL
    )


async def run_email_sync():
    try:
        manager = get_email_manager()
        await manager.sync_and_store_emails()
    except Exception as e:
        print(f"CRON JOB ERROR: {e}")
