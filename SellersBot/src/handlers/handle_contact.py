from aiogram import F, types
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import dp
from ..database import User


@dp.message(F.chat.type == ChatType.PRIVATE, F.content_type == types.ContentType.CONTACT)
async def handle_contact(message: types.Message, session: AsyncSession):
    logger.info("From user {} contact information received", message.from_user.id)
    contact = message.contact
    phone_number = contact.phone_number
    user_id = contact.user_id
    first_name = contact.first_name
    last_name = contact.last_name

    if message.from_user.id != user_id:
        logger.warning("User {} tried to share contact information of another user {}", message.from_user.id, user_id)
        await message.answer(_("you_cant_share_contact_information_of_another_user"))
        return

    logger.debug("User {} shared their contact information: {} {} {} {}", message.from_user.id, user_id, first_name, last_name, phone_number)

    logger.info("Updating user {} with contact information", user_id)
    if await User.has_shared_contacts(session, user_id):
        logger.info("User {} already shared their contact information. Updating...", user_id)
        try:
            await message.answer(_("contact_information_updated_successfully"))
        except TelegramBadRequest:
            logger.exception("Failed to send message to user {}", user_id)
        else:
            logger.success("User {} was notified about the successful update", user_id)
        return
    await User.update_user(session, user_id, first_name, last_name, phone_number)
    logger.success("User {} updated", user_id)

    try:
        await message.answer(_("contact_information_saved_successfully"))
    except TelegramBadRequest:
        logger.exception("Failed to send message to user {}", user_id)
    else:
        logger.success("User {} was notified about the successful update", user_id)
    logger.success("Contact information was handled successfully")
