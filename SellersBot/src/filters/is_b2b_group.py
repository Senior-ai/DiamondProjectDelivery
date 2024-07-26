from aiogram import types
from aiogram.filters import Filter

from ..core import B2B_GROUP_ID
from loguru import logger


class InvalidFilterParameterException(Exception):
    pass


class InvalidTypeOfB2BGroupIdConstantException(Exception):
    pass


class IsB2BGroup(Filter):
    async def __call__(self, message: types.Message) -> bool:
        logger.info("{} filter triggered in chat={}", self, message.chat.id)
        filter_result = self.is_b2b_group is (message.chat.id == B2B_GROUP_ID)
        logger.info("Filter result {}", filter_result)
        return filter_result

    def __init__(self, is_b2b_group: bool):
        if not isinstance(is_b2b_group, bool):
            raise InvalidFilterParameterException("is_b2b_group must be a boolean")
        if not isinstance(B2B_GROUP_ID, int):
            raise InvalidTypeOfB2BGroupIdConstantException("B2B_GROUP_ID must be an integer")
        self.is_b2b_group = is_b2b_group
        logger.success("Filter {} was set up", self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(is_b2b_group={self.is_b2b_group})"
