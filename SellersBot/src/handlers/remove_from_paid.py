from aiogram import types, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..tools import get_arguments
from ..core import dp
from ..database.models import ActivatedSubscription
from ..filters import ArgumentType, ArgumentsAmount, IsAdmin
from aiogram.utils.i18n import gettext as _


@dp.message(F.chat.type == ChatType.PRIVATE, IsAdmin(),
            ArgumentType(0, "int", False),
            ArgumentsAmount("=", 1),
            Command("remove_from_paid", ignore_case=True))
async def remove_from_paid(message: types.Message, session: AsyncSession):
    logger.info("remove_from_paid handler triggered")
    [user_id] = get_arguments(message.text)
    user_id = int(user_id)

    active_subscriptions = await ActivatedSubscription.get_current_active_by_user_id(session, user_id)
    if not active_subscriptions:
        logger.info("User {} does not have an active subscription. Ignoring.", user_id)
        await message.answer(_("user_does_not_have_active_subscription"))
        return

    await ActivatedSubscription.deactivate_for_user(session, user_id)
    await message.answer(_("user_removed_from_paid_successfully"))
    logger.success("User {} was removed from paid", user_id)


@dp.message(IsAdmin(),
            ArgumentsAmount("!=", 1),
            Command("remove_from_paid", ignore_case=True))
async def remove_from_paid_invalid_arguments_amount(message: types.Message):
    logger.info("remove_from_paid_invalid_arguments_amount handler triggered")
    await message.answer(_("remove_from_paid_invalid_arguments_amount"), parse_mode="markdown")
    logger.success("Invalid amount of arguments handled finished")


@dp.message(IsAdmin(),
            ArgumentType(0, "int", True),
            ArgumentsAmount("=", 1),
            Command("remove_from_paid", ignore_case=True))
async def remove_from_paid_invalid_user_id(message: types.Message):
    logger.info("remove_from_paid_invalid_user_id handler triggered")
    await message.answer(_("remove_from_paid_invalid_user_id"))
    logger.success("Invalid user id handled finished")
