# app/mail/base.py
from typing import Protocol

from app.schemas.email import EmailCreate


class IMailClient(Protocol):
    async def send_email(self, email: EmailCreate) -> bool:
        pass

    async def fetch_emails(self, top: int) -> list[dict]:
        pass
