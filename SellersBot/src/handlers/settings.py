from aiogram import types, F
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from babel import Locale
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import dp, i18n
from aiogram.utils.i18n import gettext as _

from ..services import set_language_code


@dp.message(F.chat.type == ChatType.PRIVATE, Command("settings", ignore_case=True))
async def settings_command_handler(message: types.Message):
    attached_logger = logger.bind(from_user_id=message.from_user.id, command="/settings")
    attached_logger.info("Command was received")
    attached_logger.info("User message: {}", message.text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("change_language_button"),
                    callback_data="change_language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("close_button"),
                    callback_data="close_settings"
                )
            ]
        ]
    )

    await message.answer(_("settings_message"), reply_markup=keyboard)
    attached_logger.success("Command was finished")


@dp.callback_query(F.data == "change_language")
async def change_language_button(callback_query: types.CallbackQuery):
    attached_logger = logger.bind(from_user_id=callback_query.from_user.id, command="/settings")
    attached_logger.info("change_language callback received")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("english_language_option_button"),
                    callback_data="en_language_option"
                ),
                InlineKeyboardButton(
                    text=_("hebrew_language_option_button"),
                    callback_data="he_language_option"
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("back_button"),
                    callback_data="back_to_settings_menu"
                )
            ]
        ]
    )

    try:
        await callback_query.message.edit_text(_("choose_new_language_prompt"), reply_markup=keyboard)
    except TelegramBadRequest:
        await callback_query.answer(_("settings_session_expired_message"))
    else:
        await callback_query.answer(_("choose_new_language_callback_query_reply"))


@dp.callback_query(F.data == "close_settings")
async def close_settings(callback_query: types.CallbackQuery):
    attached_logger = logger.bind(from_user_id=callback_query.from_user.id, command="/settings")
    attached_logger.info("Close settings callback received")
    await callback_query.answer()
    await callback_query.message.delete()


@dp.callback_query(F.data == "back_to_settings_menu")
async def back_to_settings_menu(callback_query: types.CallbackQuery):
    attached_logger = logger.bind(from_user_id=callback_query.from_user.id, command="/settings")
    attached_logger.info("Back to settings menu callback received")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("change_language_button"),
                    callback_data="change_language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("close_button"),
                    callback_data="close_settings"
                )
            ]
        ]
    )

    await callback_query.answer()
    await callback_query.message.edit_text(_("settings_message"), reply_markup=keyboard)


@dp.callback_query(F.data.endswith("_language_option"))
async def change_language_handler(callback_query: types.CallbackQuery, session: AsyncSession):
    attached_logger = logger.bind(from_user_id=callback_query.from_user.id, command="/settings")
    attached_logger.info("Language change callback received")

    language_code = callback_query.data[:len(callback_query.data) - len("_language_option")]

    await set_language_code(session=session, user_id=callback_query.from_user.id, language_code=language_code)
    i18n.ctx_locale.set(language_code)

    attached_logger.success("Language was changed to {}", language_code)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("english_language_option_button"),
                    callback_data="en_language_option"
                ),
                InlineKeyboardButton(
                    text=_("hebrew_language_option_button"),
                    callback_data="he_language_option"
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("back_button"),
                    callback_data="back_to_settings_menu"
                )
            ]
        ]
    )

    try:
        await callback_query.message.edit_text(_("choose_new_language_prompt"), reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "Bad Request: message is not modified" in e.message:
            await callback_query.answer()
            return
        logger.exception("Bad request exception handled")
        await callback_query.answer(_("settings_session_expired_message"))
    else:
        await callback_query.answer(_("language_was_changed_to_{}").format(Locale(language_code).display_name))
