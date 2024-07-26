from aiogram import types, F
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from ..services.process_search_query import NotEnoughDataAboutDiamondsException
from ..core import dp, bot
from loguru import logger

from ..filters import IsContactsShared
from ..services import process_search_query, SellersNotificationError
from aiogram.utils.i18n import gettext as _


@dp.message(
    F.chat.type == ChatType.PRIVATE,
    F.text,
    IsContactsShared(True)
)
async def handle_message(message: types.Message):
    logger.info("From user {} in chat {} received: {} by group message handler", message.from_user.id, message.chat.id,
                message.text)

    try:
        await message.reply(_("processing_your_search_query"))
    except TelegramBadRequest:
        logger.exception("Failed to notify client about the search query processing")
        return

    try:
        notified_sellers_amount = await process_search_query(message.text, message.from_user.id)
    except SellersNotificationError:
        logger.exception("Failed to notify sellers. This must never happen!")
        try:
            await message.reply(_("failed_to_notify_sellers_response"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about the failed sellers notification")
        else:
            logger.success("Client was notified about the failed sellers notification")
        return
    except NotEnoughDataAboutDiamondsException:
        logger.info("Not enough data about diamonds in the client`s message")
        try:
            await message.reply(_("not_enough_data_about_diamonds_response"))
        except TelegramBadRequest:
            logger.exception("Failed to reply to user about not enough data about diamonds in the message")
        else:
            logger.success("User was notified about not enough data about diamonds in the message")
        finally:
            return
    if notified_sellers_amount == 0:
        logger.info("No matching sellers found")
        try:
            await message.reply(_("no_matching_sellers_response"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about no matching sellers")
        else:
            logger.success("Client was notified about no matching sellers")
        finally:
            return
    elif notified_sellers_amount is None:
        logger.info("No diamonds in the client`s message found")
        try:
            await message.reply(_("no_diamonds_in_message_response"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about no diamonds in the message")
        else:
            logger.success("Client was notified about no diamonds in the message")
        logger.success("Message was successfully processed")
        return
    try:
        await message.reply(_("search_query_processed_response").format(notified_sellers_amount))
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the search query processing result")
    else:
        logger.info("User was notified about the search query processing result")
    logger.success("Message was successfully processed")


@dp.message(
    F.chat.type == ChatType.PRIVATE,
    ~F.text,
    IsContactsShared(True)
)
async def handle_message_without_of_text(message: types.Message):
    logger.info("Message without text from user {} in chat {} received", message.from_user.id, message.chat.id)

    try:
        await message.reply(_("message_without_text_response"))
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the message without text")
    else:
        logger.success("Message was successfully processed")


@dp.message(F.chat.type == ChatType.PRIVATE, IsContactsShared(False))
async def handle_message_without_contacts_shared(message: types.Message):
    logger.info("Message from user {} in chat {} received: {}", message.from_user.id, message.chat.id, message.text)

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
        await bot.send_message(message.from_user.id, _("contacts_not_shared_response"),
                               reply_markup=request_contact_keyboard)
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the contacts not shared")
    else:
        logger.success("Message was successfully processed")
