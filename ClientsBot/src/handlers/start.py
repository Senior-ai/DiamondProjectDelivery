from aiogram import types, F
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import User
from ..core import dp
from aiogram.utils.i18n import gettext as _


@dp.message(F.chat.type == ChatType.PRIVATE, CommandStart())
async def start_handler(message: types.Message, session: AsyncSession):
    attached_logger = logger.bind(from_user_id=message.from_user.id, command="/start")
    attached_logger.info("Command was received")
    attached_logger.info("User message: {}", message.text)
    try:
        await message.answer(_("start_message"))
        await message.answer(_("educational_message_1"))
        await message.answer(_("educational_message_2"))
        await message.answer(_("educational_message_3"))
        await message.answer(_("educational_message_4"))
    except TelegramBadRequest:
        attached_logger.exception("Failed to send messages to user")
    else:
        attached_logger.success("User was notified about the start successfully")

    if not await User.has_shared_contacts(session, message.from_user.id):
        request_contact_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text=_("share_contact_button"),
                        request_contact=True
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        try:
            await message.answer(_("please_share_your_contact_information_prompt"), reply_markup=request_contact_keyboard)
        except TelegramBadRequest:
            attached_logger.exception("Failed to send message to user")
        else:
            attached_logger.success("User was asked to share contact information")

    attached_logger.success("Command was finished")
