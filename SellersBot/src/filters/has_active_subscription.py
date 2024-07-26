from aiogram import types
from aiogram.filters import Filter
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import ActivatedSubscription


class HasActiveSubscription(Filter):
    def __init__(self, has_active_subscription: bool = True):
        if not isinstance(has_active_subscription, bool):
            raise TypeError
        self.has_active_subscription = has_active_subscription
        logger.success("Filter {} was set up", self)

    async def __call__(self, message: types.Message, session: AsyncSession):
        logger.info("{} filter triggered in chat={}", self, message.chat.id)
        user_subscriptions = await ActivatedSubscription.get_current_active_by_user_id(session, message.from_user.id)
        filter_result = self.has_active_subscription is bool(user_subscriptions)
        logger.info("Filter result {}", filter_result)
        return filter_result

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                f"(has_active_subscription={self.has_active_subscription})")