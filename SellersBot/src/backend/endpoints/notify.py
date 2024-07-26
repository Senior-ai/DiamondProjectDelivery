from uuid import UUID

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import APIRouter, Response
from loguru import logger

from ...services.users import get_gettext
from ...core import bot, B2B_GROUP_ID
from ...database.loader import sessionmaker
from ..router import router
from ...database.models import ContactsPurchaseTokenInformation, GeneratedToken, User

notify_router = APIRouter(prefix="/notify")


type SuccessfullyNotifiedSellersAmount = int


@notify_router.get('/{seller}/successful_subscription_renewal', status_code=200)
async def successful_subscription_renewal(seller: int):
    logger.success("Subscription renewal notification request received")

    async with sessionmaker() as session:
        _ = await get_gettext(session, seller)
    try:
        await bot.send_message(seller, _("subscription_activated_notification"))
    except TelegramBadRequest:
        logger.error("Failed to send notification to user {}", seller)
        return Response(status_code=400, content="Failed to send notification to user")
    else:
        logger.success("Notification sent to user {}", seller)

    try:
        invite_link = await bot.create_chat_invite_link(B2B_GROUP_ID)
    except TelegramBadRequest:
        logger.error("Failed to get group chat invite link")
    else:
        logger.debug("Invite link: {}", invite_link.invite_link)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("b2b_group_link_button"),
                        url=invite_link.invite_link
                    )
                ]
            ]
        )

        await bot.send_message(seller, _("b2b_group_link_message"), reply_markup=keyboard)


@notify_router.get('/contact_purchase/{token_value}', status_code=200)
async def contacts_purchase(token_value: str):
    logger.success("Contacts purchase request received")

    async with sessionmaker() as session:
        token_author = await GeneratedToken.get_token_author(session, token_value)

        if token_author is None:
            logger.error("Token {} not found", token_value)
            return Response(status_code=404, content="Token not found")

        client_id = (await ContactsPurchaseTokenInformation.get(session, UUID(token_value))).client_id

        _ = await get_gettext(session, token_author)

        client = await User.get(session, client_id)

        if client is None:
            logger.error("Client {} not found. Payment token: {}. This must never happen!", client_id, token_value)
            await bot.send_message(token_author, _("client_not_found_notification"))
            return Response(status_code=404, content="Client not found")

        try:
            logger.info("Sending contact to seller {}", token_author)
            await bot.send_contact(chat_id=token_author, phone_number=client.phone_number, first_name=client.first_name,
                                   last_name=client.last_name)
            # await bot.send_contact(chat_id=client_id, phone_number="111111111", first_name="Some", last_name="Client")
        except TelegramBadRequest:
            logger.error("Failed to send contact to client {}", client_id)
            return Response(status_code=400, content="Failed to send contact to client")
        else:
            logger.success("Contact sent to seller {}", client_id)

    logger.success("Contacts purchase request processed")


router.include_router(notify_router)
