from aiogram import types, F
from aiogram.enums import MessageEntityType, ChatType

from ..core import dp
from loguru import logger
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _


@dp.message(F.chat.type == ChatType.PRIVATE, F.entities[...].type == MessageEntityType.BOT_COMMAND)
async def unknown_command_handler(message: types.Message):
    logger.info("From user {} unknown command received: {}", message.from_user.id, message.text)
    if message.chat.type == "private":
        await message.reply(_("unknown_command_error"))
        logger.success("User was notified about the unknown command successfully")
    logger.success("Unknown command was handled successfully")


@dp.callback_query()
async def unknown_callback_handler(callback_query: types.CallbackQuery):
    logger.info("From user {} unknown callback received: {}", callback_query.from_user.id, callback_query.data)
    try:
        await callback_query.message.edit_reply_markup(None)
    except TelegramBadRequest:
        logger.info("Telegram bad request exception was handled after edit reply markup attempt.")
    await callback_query.answer(_("lost_context_error"))
    logger.success("User was notified about the lost context successfully")
