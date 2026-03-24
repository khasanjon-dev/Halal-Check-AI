import logging
import os

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Settings:
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True if os.getenv("DEBUG") == "True" else False
    PROJECT_NAME: str = "Halal Checker API"

    # DATABASE
    SQL_URL: str = os.getenv("SQL_URL")
    SQL_ECHO: bool = True

    # GEMINI API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str= os.getenv("GEMINI_MODEL")


settings = Settings()
