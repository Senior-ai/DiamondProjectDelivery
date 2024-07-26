from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.create_payment_url import PaymentLinkGenerationError
from ..database.models.enums import PaymentPurpose
from ..database.models import ActivatedSubscription
from ..services import create_payment_url
from ..core import dp
from aiogram.utils.i18n import gettext as __


@dp.message(F.chat.type == ChatType.PRIVATE, Command("start", ignore_case=True))
async def start_handler(message: types.Message, session: AsyncSession):
    attached_logger = logger.bind(from_user_id=message.from_user.id, command="/start")
    attached_logger.info("Command was received")
    attached_logger.info("User message: {}", message.text)
    await message.answer(__("start_message"))

    activated_subscriptions = await ActivatedSubscription.get_current_active_by_user_id(session, message.from_user.id)
    logger.debug(activated_subscriptions)
    logger.debug(type(activated_subscriptions))

    if len(activated_subscriptions) == 0:
        attached_logger.info("User {} has not got active subscription plan", message.from_user.id)

        try:
            [payment_link, _] = await create_payment_url(session, message.from_user.full_name, message.from_user.id,
                                                         PaymentPurpose.SUBSCRIPTION_RENEWAL)
        except PaymentLinkGenerationError:
            attached_logger.exception("Failed to generate payment link")
            try:
                await message.answer(
                    __("Some error occurred and we can't renew you a subscription. Please try again later."))
            except TelegramBadRequest:
                attached_logger.exception(
                    "Failed to notify user about the payment link generation error. This must never happen!")
            else:
                attached_logger.success("User was notified about the payment link generation error")
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=__("activate_subscription_button"),
                        url=payment_link
                    )
                ]
            ]
        )

        await message.answer(__("activate_subscription_suggestion"), reply_markup=keyboard)

    attached_logger.success("Command was finished")
