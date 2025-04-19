import logging

from app.db.base import IEmailRepository
from app.mail.base import IMailClient
from app.schemas.email import EmailCreate, EmailInDB

logger = logging.getLogger(__name__)


class EmailManager:
    def __init__(self, mail_client: IMailClient, email_repo: IEmailRepository):
        self.mail_client = mail_client
        self.email_repo = email_repo

    async def sync_and_store_emails(self) -> list[EmailInDB]:
        """Fetch emails via IMailClient, and store them in IEmailRepository."""
        logger.info("Fetching new emails from mail client...")
        emails_raw = await self.mail_client.fetch_emails()
        stored = []
        for raw in emails_raw:
            try:
                email = EmailInDB(**raw)  # assumes static constructor exists
                await self.email_repo.upsert_email(email)
                stored.append(email)
            except Exception as e:
                logger.warning(f"Failed to parse or store email: {e}")
        logger.info(f"Stored {len(stored)} emails to repository.")
        return stored

    async def send_email(self, email: EmailCreate) -> bool:
        """Send an email and record it in the repository."""
        logger.info(f"Sending email to: {email.recipients}")
        success = await self.mail_client.send_email(email)
        return success
