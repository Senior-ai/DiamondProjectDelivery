from aiogram import types
from aiogram.filters import Filter
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import Admin


class IsAdmin(Filter):
    async def __call__(self, message: types.Message, session: AsyncSession) -> bool:
        logger.info("{} filter triggered in chat={}", self, message.chat.id)
        filter_result = await Admin.check_user(session, message.from_user.id)
        logger.info("Filter result {}", filter_result)
        return filter_result

    def __init__(self):
        logger.success("Filter {} was set up", self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
