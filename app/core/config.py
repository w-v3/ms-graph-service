import logging
import os
import sys
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
# from dotenv import load_dotenv
# load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env.docker.new")
# print("Before clearing:")
# for key in ["CLIENT_ID", "CLIENT_SECRET", "TENANT_ID", "USER_EMAIL", "USER_PASSWORD"]:
#     print(f"{key}: {os.getenv(key)}")

# # Clear the variables
# for key in ["CLIENT_ID", "CLIENT_SECRET", "TENANT_ID", "USER_EMAIL", "USER_PASSWORD"]:
#     os.environ.pop(key, None)

# print("After clearing:")
# for key in ["CLIENT_ID", "CLIENT_SECRET", "TENANT_ID", "USER_EMAIL", "USER_PASSWORD"]:
#     print(f"{key}: {os.getenv(key)}")
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Microsoft Graph API Settings
    # CLIENT_ID: str = "349f8407-8489-4819-941a-d7f0d338eba8"
    
    # TENANT_ID: str = "consumers"
    # USER_EMAIL: str = "kavidaapp@outlook.com"
    # MS_GRAPH_API_URL: str = "https://graph.microsoft.com/v1.0/me"
    # MS_GRAPH_AUTH_URL: str = "https://login.microsoftonline.com"
    # SCOPES: list[str] = [
    #     "https://graph.microsoft.com/User.Read",
    #     "https://graph.microsoft.com/Mail.Read",
    #     "https://graph.microsoft.com/Mail.Send",
    # ]
    # # MongoDB Settings
    # MONGODB_URI: str = "mongodb://localhost:27017"
    # DATABASE_NAME: str = "email_service"
    # MONGO_URI: str = "mongodb://admin:password123@localhost:27017"
    # # API Settings
    # API_V1_STR: str = "/api/v1"

    CLIENT_ID: str = Field(..., env="CLIENT_ID")
    TENANT_ID: str = Field(..., env="TENANT_ID")
    USER_EMAIL: str = Field(..., env="USER_EMAIL")
    MS_GRAPH_API_URL: str = Field(..., env="MS_GRAPH_API_URL")
    MS_GRAPH_AUTH_URL: str = Field(..., env="MS_GRAPH_AUTH_URL")
    RAW_SCOPES: str = Field(..., validation_alias="SCOPES")

    # MongoDB Settings
    #MONGODB_URI: str = Field(..., env="MONGODB_URI")
    #MONGO_URI: str = Field(..., env="MONGO_URI")
    DATABASE_NAME: str = Field(..., env="DATABASE_NAME")
    MONGO_AUTH_USERNAME: str = Field(..., env="MONGO_AUTH_USERNAME")
    MONGO_AUTH_PASSWORD: str = Field(..., env="MONGO_AUTH_PASSWORD")
    MONGO_SERVER_ADDRESS: str = Field(..., env="MONGO_SERVER_ADDRESS")
    MONGO_SERVER_PORT: str = Field(..., env="MONGO_SERVER_PORT")
    # API Settings
    API_V1_STR: str = Field(..., env="API_V1_STR")
    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")

    # Email Polling
    EMAIL_RETRIEVAL_INTERVAL_MINUTES: int = Field(..., env="EMAIL_RETRIEVAL_INTERVAL_MINUTES")

    ## OTHER VARIBALES NOT NECESSARILY ENV VARS
    COLLECTIONS: List[str] = ["users" , "emails"]

    class Config:
        # env_file = str(Path(__file__).parent.parent.parent / ".env.docker.new")
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    @property
    def SCOPES(self) -> List[str]:
        return [scope.strip() for scope in self.RAW_SCOPES.split(",")]

    @property
    def MONGODB_URI(self) -> str:
        return f"mongodb://{self.MONGO_AUTH_USERNAME}:{self.MONGO_AUTH_PASSWORD}@{self.MONGO_SERVER_ADDRESS}:{self.MONGO_SERVER_PORT}"

    @property
    def MONGO_URI(self) -> str:
        return f"mongodb://{self.MONGO_AUTH_USERNAME}:{self.MONGO_AUTH_PASSWORD}@{self.MONGO_SERVER_ADDRESS}:{self.MONGO_SERVER_PORT}"


    @classmethod
    def _get_env_var_names(cls) -> List[str]:
        return [
            field.alias.upper() if field.alias else name.upper()
            for name, field in cls.__fields__.items()
        ]

    @classmethod
    def _unset_env_vars(cls):
        for var in cls._get_env_var_names():
            if var in os.environ:
                del os.environ[var]
                print(f"Unset: {var}")

    @classmethod
    def _print_env_vars(cls):
        print("\n🔍 Current Environment Variables:")
        for var in cls._get_env_var_names():
            print(f"{var}: {os.getenv(var, '<NOT SET>')}")

    def __new__(cls, *args, **kwargs):
        cls._unset_env_vars()  # Before instantiation
        instance = super().__new__(cls)  # Create instance
        # __init__ will run right after this
        return instance  # After instantiation


# Debug: Print environment variables

settings = Settings()
print(settings.MONGO_SERVER_ADDRESS)
print(settings.MONGO_URI)
