# app/db/base.py
from typing import Protocol, runtime_checkable

from app.schemas.email import EmailInDB


@runtime_checkable
class IEmailRepository(Protocol):
    async def upsert_email(self, email: EmailInDB) -> None:
        pass

    async def list_recent_emails(
        self,
        filter_query: dict = None,
        limit: int = 10,
    ) -> list[EmailInDB]:
        pass
