import asyncio

import uvicorn
from loguru import logger

from .core import BACKEND_HOST, BACKEND_PORT, LOG_LEVEL, setup_logging, ENVIRONMENT
from .api import app
from .database.loader import init_database


async def main() -> None:
    logger.info(f"Starting server at {BACKEND_HOST}:{BACKEND_PORT}")
    logger.info(f"Logging level is {LOG_LEVEL}")
    config = uvicorn.Config(app, host=BACKEND_HOST, port=BACKEND_PORT, log_level=LOG_LEVEL)
    server = uvicorn.Server(config)
    setup_logging()
    logger.add("logs/colorized_logs.log", rotation="5 MB", enqueue=True, colorize=True, level=LOG_LEVEL)
    logger.add("logs/logs.log", rotation="50 MB", enqueue=True, level=LOG_LEVEL)
    await init_database(ENVIRONMENT == "development")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
