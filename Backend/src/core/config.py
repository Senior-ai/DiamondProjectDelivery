import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv()
BACKEND_HOST = getenv("backend_host")
BACKEND_PORT = int(getenv("backend_port"))

DB_USER = getenv("db_user")
DB_PASSWORD = getenv("db_password")
DB_HOST = getenv("db_host")
DB_PORT = getenv("db_port")
DB_NAME = getenv("db_name")

sync_database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
async_database_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SELLERS_BOT_HOST = getenv("sellers_bot_host")
SELLERS_BOT_PORT = int(getenv("sellers_bot_port"))

CLIENTS_BOT_HOST = getenv("clients_bot_host")
CLIENTS_BOT_PORT = int(getenv("clients_bot_port"))

STRING_LOG_LEVEL = getenv("log_level", "DEBUG")
LOG_LEVEL = logging.getLevelName(STRING_LOG_LEVEL)

ENVIRONMENT = getenv("environment")
assert ENVIRONMENT in ["production", "development"]

BACKEND_ACCESS_TOKEN = getenv("backend_access_token")
