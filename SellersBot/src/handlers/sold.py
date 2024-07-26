from aiogram import types, F
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.diamonds import delete_diamond_for_user, is_user_owns_diamond
from ..tools import get_arguments
from ..core import dp
from ..filters import HasActiveSubscription, ArgumentType, ArgumentsAmount
from aiogram.utils.i18n import gettext as _


@dp.message(F.chat.type == ChatType.PRIVATE,
            Command("sold", ignore_case=True),
            HasActiveSubscription(),
            ArgumentType(0, "str"),
            ArgumentsAmount("=", 1))
async def sold(message: types.Message, session: AsyncSession):
    logger.info("/sold handler triggered by user {} with message: {}", message.from_user.id, message.text)
    [diamond_stock] = get_arguments(message.text)
    is_owner = await is_user_owns_diamond(session, message.from_user.id, diamond_stock)
    if not is_owner:
        try:
            await message.answer(_("diamond_is_already_sold_or_was_not_in_your_stock"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about the diamond is already sold or was not in the stock")
        finally:
            return
    await delete_diamond_for_user(session, message.from_user.id, diamond_stock)
    logger.success("Diamond {} was sold by user {}", diamond_stock, message.from_user.id)
    try:
        await message.answer(_("diamond_sold_successfully"))
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the successful diamond selling")
    finally:
        logger.success("/sold handler finished")
        return


@dp.message(F.chat.type == ChatType.PRIVATE,
            Command("sold", ignore_case=True),
            HasActiveSubscription(),
            ArgumentType(0, "str", inverted=True),
            ArgumentsAmount("=", 1))
async def sold_for_invalid_argument_type(message: types.Message):
    logger.info("/sold handler for invalid argument type triggered by user {} with message: {}", message.from_user.id,
                message.text)
    await message.answer(_("invalid_argument_of_sold_command"), parse_mode="markdown")
    logger.success("/sold handler for invalid argument type finished")


@dp.message(F.chat.type == ChatType.PRIVATE,
            Command("sold", ignore_case=True),
            HasActiveSubscription(),
            ArgumentsAmount("!=", 1))
async def sold_with_invalid_amount_of_arguments(message: types.Message):
    logger.info("/sold handler for invalid amount of arguments triggered by user {} with message: {}",
                message.from_user.id, message.text)
    await message.answer(_("invalid_amount_of_sold_command_arguments"), parse_mode="markdown")
    logger.success("/sold handler for invalid amount of arguments finished")

@dp.message(F.chat.type == ChatType.PRIVATE,
            Command("sold", ignore_case=True), HasActiveSubscription(False))
async def sold_without_of_subscription(message: types.Message):
    logger.info("/sold handler triggered by user {} with message {}, but without of subscription", message.from_user.id,
                message.text)
    await message.answer(_("cant_use_sold_command_without_of_subscription"))
    logger.success("/sold handler for user without of a subscription finished")
