from aiogram.enums import ChatType
from aiogram.filters import Command

from ..core import dp
from aiogram import types, F
from loguru import logger

from aiogram.utils.i18n import gettext as _


@dp.message(F.chat.type == ChatType.PRIVATE, Command("help", ignore_case=True))
async def help_or_start_handler(message: types.Message):
    attached_logger = logger.bind(from_user_id=message.from_user.id, command="/help")
    attached_logger.info("Command was received")
    attached_logger.info("User message: {}", message.text)
    await message.answer(_("help_message"), parse_mode="markdown")
    attached_logger.success("Command was finished")
