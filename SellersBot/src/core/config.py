import logging
from os import getenv
from pathlib import Path


BOT_TOKEN = getenv("bot_token")
B2B_GROUP_ID = int(getenv("b2b_group_id"))

LOCALES_DIR = localedir = Path(__file__).parent.parent.parent.absolute() / 'locale'
I18N_DOMAIN = "messages"
DEFAULT_LOCALE = "en"

BACKEND_HOST = getenv("bot_backend_host")
BACKEND_PORT = int(getenv("bot_backend_port"))

DB_USER = getenv("db_user")
DB_PASSWORD = getenv("db_password")
DB_HOST = getenv("db_host")
DB_PORT = getenv("db_port")
DB_NAME = getenv("db_name")

sync_database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
async_database_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

OPENAI_API_KEY = getenv("openai_api_key")
JSON_EXTRACTOR_ASSISTANT_ID = getenv("json_extractor_assistant_id")

PAYMENT_PROVIDER_TERMINAL = int(getenv("payment_provider_terminal"))
PAYMENT_PROVIDER_USERNAME = getenv("payment_provider_api_name")

STRING_LOG_LEVEL = getenv("log_level", "DEBUG")
LOG_LEVEL = logging.getLevelName(STRING_LOG_LEVEL)

BACKEND_URL = getenv("backend_url")
