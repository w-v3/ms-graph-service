import datetime
import logging

from app.db.base import IEmailRepository
from app.db.connection.base import IConnectionManager
from app.schemas.email import EmailInDB

logger = logging.getLogger(__name__)

from app.schemas.email import EmailCreate


class MongoEmailRepository(IEmailRepository):
    def __init__(self, manager: IConnectionManager):
        self.manager = manager

    async def upsert_email(self, email: EmailInDB) -> None:
        db = await self.manager.connect()
        # assert "_id" in email.model_dump(by_alias=True)
        # print(email.model_dump(by_alias=True))
        print("ID used in upsert:", email.id)

        await db.emails.update_one(
            {"_id": email.id},
            {"$set": email.model_dump(by_alias=True)},
            upsert=True,
        )
        did = await db.emails.distinct("_id")
        alist = await db.emails.find({"_id": email.id}).to_list(None)
        print(len(did), len(alist))

    async def list_recent_emails(self, limit: int = 10):
        db = await self.manager.connect()
        cursor = db.emails.find().sort("receivedDateTime", -1).limit(limit)
        return [EmailInDB(**doc) async for doc in cursor]

    async def save_sent_email(self, email: EmailCreate) -> None:
        db = await self.manager.connect()
        await db.emails.insert_one(
            {
                "_id": str(email.id),
                "subject": email.subject,
                "body": {"content": email.body, "contentType": "HTML"},
                "toRecipients": email.recipients,
                "sentDateTime": datetime.utcnow(),
                "status": "Sent",
            },
        )
