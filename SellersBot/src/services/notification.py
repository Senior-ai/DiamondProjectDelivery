from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.enums import PaymentPurpose
from ..database.models.processing_types import ExtractedDiamond
from .diamond_utils import generate_text_table, generate_csv_content
from ..core import bot
from ..database.models import ActivatedSubscription, ContactsPurchaseTokenInformation, Diamond, User
from .users import get_gettext
from .create_payment_url import create_payment_url
from loguru import logger


async def notify_diamonds_owner(session: AsyncSession, interested_user_id: int,
                                diamonds_by_sellers: dict[int, list[Diamond]], diamonds: list[ExtractedDiamond],
                                free_notification: bool = False) -> int:
    successfully_notified_sellers_amount = 0

    for seller, similar_diamonds in diamonds_by_sellers.items():
        # if interested_user_id == seller:
        #     logger.info("Seller {} is the same as the interested user. Ignoring.", seller)
        #     continue
        active_subscriptions = await ActivatedSubscription.get_current_active_by_user_id(session, seller)
        if not active_subscriptions:
            logger.info("Seller {} does not have an active subscription. Ignoring.", seller)
            continue

        _ = await get_gettext(session, seller)

        queried_diamonds = "\n".join(diamond.to_user_friendly_string(_) for diamond in diamonds)
        logger.debug("Queried diamonds: {}", queried_diamonds)
        table = generate_text_table(similar_diamonds)
        logger.debug("Table: {}", table)

        csv_buffer = generate_csv_content(similar_diamonds)

        if free_notification:
            message_id = "free_interested_client_present_notification"
        else:
            message_id = "interested_client_present_notification"

        message = _(message_id).format(queried_diamonds, table)
        input_file = BufferedInputFile(csv_buffer, filename="similar_diamonds.csv")

        if free_notification:
            interested_user = await User.get(session, interested_user_id)

            try:
                await bot.send_message(seller, message, parse_mode="markdown")
                await bot.send_document(
                    chat_id=seller,
                    document=input_file,
                    caption=_("file_with_complete_list_of_similar_diamonds")
                )
                await bot.send_contact(
                    seller,
                    phone_number=interested_user.phone_number,
                    first_name=interested_user.first_name,
                    last_name=interested_user.last_name
                )
            except TelegramBadRequest:
                logger.exception("Failed to send free notification to seller {}", seller)
            else:
                successfully_notified_sellers_amount += 1
                logger.success("Free notification sent to seller {}", seller)
        else:
            try:
                seller_full_name = (await bot.get_chat(seller)).full_name
            except TelegramBadRequest:
                seller_full_name = ""

            [payment_link, token_value] = await create_payment_url(session, seller_full_name, seller,
                                                                   PaymentPurpose.CONTACTS_PURCHASE)
            await ContactsPurchaseTokenInformation.add(session, token_value, interested_user_id)

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("buy_client_contacts_button"),
                            url=payment_link
                        )
                    ]
                ]
            )

            try:
                await bot.send_message(seller, message, reply_markup=keyboard, parse_mode="markdown")
                await bot.send_document(
                    chat_id=seller,
                    document=input_file,
                    caption=_("file_with_complete_list_of_similar_diamonds")
                )
            except TelegramBadRequest:
                logger.exception("Failed to send paid notification to seller {}", seller)
            else:
                successfully_notified_sellers_amount += 1
                logger.success("Paid notification sent to seller {}", seller)
    return successfully_notified_sellers_amount
