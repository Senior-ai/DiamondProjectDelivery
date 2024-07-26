from uuid import uuid4

from asyncpg import Connection
from loguru import logger
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy_utils import database_exists, create_database

from .defaults import add_all_defaults
from .models import Base
from ..core.config import sync_database_url, async_database_url


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


def get_engine(async_url: URL | str = async_database_url) -> AsyncEngine:
    async_engine = create_async_engine(
        url=async_url,
        echo=False,
        pool_size=0,
        connect_args={
            "connection_class": CConnection,
        },
    )

    return async_engine


def get_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def init_models():
    logger.info("Initializing models")
    async with engine.begin() as conn:
        logger.warning("Dropping all tables")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Creating all tables")
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def add_defaults():
    logger.info("Adding defaults")
    async with sessionmaker() as session:
        await add_all_defaults(session)
        await session.commit()
        logger.success("Defaults were added")


async def init_database(fresh_init: bool = False) -> None:
    if fresh_init:
        if not database_exists(sync_database_url):
            logger.info("Creating database")
            create_database(sync_database_url)
            logger.success("Database was created")
        else:
            logger.info("Database was found")
        await init_models()
        await add_defaults()
    else:
        if not database_exists(sync_database_url):
            logger.info("Creating database")
            create_database(sync_database_url)
            logger.success("Database was created")
            await init_models()
            await add_defaults()
        else:
            logger.info("Database was found")

    logger.success("Database initialization was finished")


engine = get_engine(async_url=async_database_url)
sessionmaker = get_sessionmaker(engine)
