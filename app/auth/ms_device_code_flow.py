# app/auth/ms_device_code_flow.py
import logging
import os
import sys

import msal

from app.auth.base import IAuthFlow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class DeviceCodeFlow(IAuthFlow):
    def __init__(
        self,
        client_id: str,
        tenant: str,
        scopes: list[str],
        auth_url: str,
        cache_file="token_cache.json",
    ):
        self.client_id = client_id
        self.authority = f"{auth_url}/{tenant}"
        self.scopes = scopes
        self.cache_file = cache_file
        self.token_cache = msal.SerializableTokenCache()

        self._load_token_cache()

        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.token_cache,
        )

    def acquire_token(self):
        accounts = self.app.get_accounts()
        result = None
        if accounts:
            logger.info(f"acquire_token: found accounts {accounts!r}")
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            logger.info(f"acquire_token: silent result = {result!r}")
            self._save_token_cache()
            return result
        # 2) If silent failed or no access_token, always do the device‐code flow
        if not result or "access_token" not in result:
            logger.info("acquire_token: silent failed, initiating device flow")

            flow = self.app.initiate_device_flow(scopes=self.scopes)

            logger.info(f"acquire_token: device_flow response = {flow!r}")
            logger.info(f"Device‑flow response: {flow!r}")

            if "user_code" not in flow:
                err = flow.get("error", "<no‑error>")
                desc = flow.get("error_description", "<no‑description>")
                raise Exception(f"Device‑flow init failed: {err} — {desc}")

            logger.info(flow["message"])
            result = self.app.acquire_token_by_device_flow(flow)
            logger.info(f"acquire_token: device_flow token result = {result!r}")
            self._save_token_cache()
            return result

        if not result or "access_token" not in result:
            logger.error(f"acquire_token: final result invalid = {result!r}")
            raise Exception(f"Token acquisition failed: {result}")

        #  if "access_token" in result:
        #     if self._save_token_cache():
        #         logger.info("acquire_token: success, returning token")
        #         return result
        # else:
        #     raise Exception(f"Token acquisition failed: {result}")

    def _load_token_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file) as f:
                self.token_cache.deserialize(f.read())

    def _save_token_cache(self):
        if self.token_cache.has_state_changed:
            with open(self.cache_file, "w") as f:
                f.write(self.token_cache.serialize())
