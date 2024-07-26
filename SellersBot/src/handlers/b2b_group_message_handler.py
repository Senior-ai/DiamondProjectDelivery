from aiogram import types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import ActivatedSubscription
from ..filters.is_contacts_shared import IsContactsShared
from ..services.process_search_query import SellersNotificationError, NotEnoughDataAboutDiamondsException, \
    process_search_query, NoDiamondsInMessage
from ..filters import IsB2BGroup
from ..core import dp
from loguru import logger
from aiogram.utils.i18n import gettext as _


@dp.message(IsB2BGroup(True), F.text, IsContactsShared(True))
async def handle_b2b_group_message_with_contacts(message: types.Message, session: AsyncSession):
    logger.info("From user {} in chat {} received: {} by group message handler", message.from_user.id, message.chat.id,
                message.text)

    logger.info("Checking user's subscription")
    if not await ActivatedSubscription.get_current_active_by_user_id(session, message.from_user.id):
        logger.info("User {} has no active subscription", message.from_user.id)
        try:
            forwarded_message = await message.forward(message.from_user.id)
            await forwarded_message.reply(_("no_active_subscription_found_error"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about no active subscription")
        else:
            logger.success("User was notified about no active subscription")
        return

    try:
        notified_sellers_amount = await process_search_query(session, message.text, message.from_user.id,
                                                             free_notification=True)
    except SellersNotificationError:
        logger.exception("Failed to notify sellers. This must never happen!")

        try:
            forwarded_message = await message.forward(message.from_user.id)
            await forwarded_message.reply(_("failed_to_notify_sellers_response"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about the failed sellers notification")
        else:
            logger.success("Client was notified about the failed sellers notification")
        return
    except NotEnoughDataAboutDiamondsException:
        logger.info("Not enough data about diamonds in the client`s message")

        try:
            forwarded_message = await message.forward(message.from_user.id)
            await forwarded_message.reply(_("not_enough_data_about_diamonds_response"))
        except TelegramBadRequest:
            logger.exception("Failed to reply to user about not enough data about diamonds in the message")
        else:
            logger.success("User was notified about not enough data about diamonds in the message")
        finally:
            return
    except NoDiamondsInMessage:
        logger.info("No diamonds in the client`s message found")
        return

    if notified_sellers_amount == 0:
        logger.info("No matching sellers found")

        try:
            forwarded_message = await message.forward(message.from_user.id)
            await forwarded_message.reply(_("no_matching_sellers_response"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about no matching sellers")
        else:
            logger.success("Client was notified about no matching sellers")
        finally:
            return
    try:
        forwarded_message = await message.forward(message.from_user.id)
        await forwarded_message.reply(_("search_query_processed_response").format(notified_sellers_amount))
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the search query processing result")
    else:
        logger.info("User was notified about the search query processing result")
    logger.success("Message was successfully processed")


@dp.message(IsB2BGroup(True), F.text, IsContactsShared(False))
async def handle_b2b_group_message_without_contacts(message: types.Message):
    logger.info("Message from user {} in chat {} received: {}", message.from_user.id, message.chat.id, message.text)

    try:
        forwarded_message = await message.forward(message.from_user.id)
    except TelegramBadRequest:
        logger.exception("Failed to forward the message")
        return
    else:
        logger.info("Message was successfully forwarded")

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
        await forwarded_message.reply(_("contacts_not_shared_response"), reply_markup=request_contact_keyboard)
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the contacts not shared")
    else:
        logger.success("Message was successfully processed")
