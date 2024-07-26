from aiogram import types
from aiogram.filters import Filter
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import User


class IsContactsShared(Filter):
    def __init__(self, is_contacts_shared: bool = True):
        if not isinstance(is_contacts_shared, bool):
            raise TypeError
        self.is_contacts_shared = is_contacts_shared
        logger.success("Filter {} was set up", self)

    async def __call__(self, message: types.Message, session: AsyncSession):
        filter_result = self.is_contacts_shared is await User.has_shared_contacts(session, message.from_user.id)
        logger.info("{} filter result {}", self, filter_result)
        return filter_result

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                f"(is_contacts_shared={self.is_contacts_shared})")
