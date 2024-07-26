import uvicorn

from .core import LOG_LEVEL, setup_logging
from .backend import fastapi_instance
from .middlewares.registration import RegistrationMiddleware
from .middlewares.database import DatabaseMiddleware
from .core import i18n
from .middlewares import CustomI18nMiddleware
from .handlers import dp
import asyncio
from loguru import logger
from .core import bot


async def on_startup() -> None:
    logger.info("On startup event was triggered")

    logger.info("Starting FastAPI server...")
    config = uvicorn.Config(fastapi_instance, host="0.0.0.0", port=8001, log_level=LOG_LEVEL)
    server = uvicorn.Server(config)
    logger.info("Setting up uvicorn and global logging...")
    setup_logging()
    logger.add("logs/colorized_logs.log", rotation="5 MB", enqueue=True, colorize=True, level=LOG_LEVEL)
    logger.add("logs/logs.log", rotation="50 MB", enqueue=True, level=LOG_LEVEL)
    logger.success("FastAPI server and logging configured")

    asyncio.create_task(server.serve())


async def on_shutdown() -> None:
    logger.info("On shutdown event was triggered")
    await bot.close()


async def main() -> None:
    logger.info("Starting the bot`s polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting the bot...")
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.outer_middleware(DatabaseMiddleware())
    dp.message.middleware(RegistrationMiddleware())
    dp.message.middleware(CustomI18nMiddleware(i18n))
    dp.callback_query.outer_middleware(DatabaseMiddleware())
    dp.callback_query.middleware(RegistrationMiddleware())
    dp.callback_query.middleware(CustomI18nMiddleware(i18n))
    asyncio.run(main())
