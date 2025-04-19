# app/mail/ms_graph_client.py
from datetime import UTC, datetime, timedelta
import logging

import requests

from app.auth.base import IAuthFlow
from app.mail.base import IMailClient
from app.schemas.email import EmailCreate

logger = logging.getLogger(__name__)


class GraphMailClient(IMailClient):
    def __init__(self, auth_flow: IAuthFlow, user_email: str , api_url:str):
        logger.info("=" * 50)
        logger.info("Initializing Microsoft GraphAPIService with auth flow")
        self.auth_flow = auth_flow
        self.user_email = user_email
        self.last_fetch_time: str | None = None
        self.token = self.auth_flow.acquire_token()
        self.api_url = api_url


    def _get_headers(self):
        logger.info(f"token accquired {self.token['access_token']}")
        self.token = self.auth_flow.acquire_token()
        logger.info(f"token accquired {self.token['access_token']}")
        return {
            "Authorization": f"Bearer {self.token['access_token']}",
            "Content-Type": "application/json",
        }

    async def send_email(self, email: EmailCreate) -> bool:
        try:
            payload = {
                "message": {
                    "subject": email.subject,
                    "body": {"contentType": "HTML", "content": email.body},
                    "toRecipients": [
                        {"emailAddress": {"address": addr}} for addr in email.recipients
                    ],
                },
            }
            headers = self._get_headers()
            logger.info("--" * 60)
            logger.info(f"Sending email using user: {self.user_email}")
            logger.info(f"Message: {payload}")

            response = requests.post(
                f'{self.api_url}/sendMail',
                headers=headers,
                json=payload,
            )
            logger.info(f"Response: {response}")
            if response.status_code == 202:
                logger.info("Email sent successfully")
                logger.info(f"Response: {response}")
                return True
            logger.error(f"Failed to send: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e!s}")
            return False

    async def fetch_emails(self) -> list[dict]:
        try:
            logger.info(f"Retrieving emails for user: {self.user_email}")
            headers = self._get_headers()

            # Ensure the datetime has timezone info
            if self.last_fetch_time is not None:
                fetch_time_dt = self.last_fetch_time
                if fetch_time_dt.tzinfo is None:
                    fetch_time_dt = fetch_time_dt.replace(tzinfo=UTC)
            else:
                fetch_time_dt = datetime.utcnow().replace(tzinfo=UTC) - timedelta(
                    days=1,
                )

            fetch_time = fetch_time = (
                fetch_time_dt.replace(microsecond=0)
                .astimezone(UTC)
                .strftime("%Y-%m-%dT%H:%M:%SZ")
            )

            logger.info(f"Using fetch time: {fetch_time}")
            filter_query = f"receivedDateTime ge {fetch_time}"

            url = f'{self.api_url}/messages?$filter={filter_query}&$orderby=receivedDateTime asc'

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                messages = response.json().get("value", [])
                logger.info(f"fetched {len(messages)} new emails")
                if messages:
                    # Update last_fetch_time based on the latest email received
                    latest_time_str = messages[-1]["receivedDateTime"]
                    self.last_fetch_time = datetime.fromisoformat(
                        latest_time_str.replace("Z", "+00:00"),
                    )
                return messages

            logger.error(f"Failed to fetch: {response.status_code} - {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving emails: {e!s}")
            return []
