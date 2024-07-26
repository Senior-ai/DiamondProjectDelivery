import io
from collections import defaultdict

from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import INSTRUCTIONS_FILE_PATH
from ..services import (InvalidCSVFileError, TotalDiamondsLimitExceededError, DiamondsPerLoadLimitExceededError,
                        NoActiveSubscriptionFoundError, process_uploaded_diamonds_csv)
from ..services.diamond_utils import generate_csv_content, generate_text_table
from ..core import dp, bot
from aiogram import types, F
from aiogram.types import ContentType, BufferedInputFile
from aiogram.utils.i18n import gettext as _

from loguru import logger


unsuccessful_attempts = defaultdict(int)


@dp.message(F.chat.type == ChatType.PRIVATE, F.content_type == ContentType.DOCUMENT)
async def csv_file_upload(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    logger.info("Received a document from user {}", user_id)

    if message.document.file_size > 1024 * 1024:
        await handle_error_message(user_id, message, _("file_too_large_error"))
        return

    if message.document.mime_type not in ["text/csv", "text/comma-separated-values"]:
        logger.debug("Received file type {}", message.document.mime_type)
        await handle_error_message(user_id, message, _("invalid_file_type_error"))
        return

    stream = io.BytesIO()
    await bot.download(message.document, destination=stream)
    text_io = io.TextIOWrapper(stream, encoding='utf-8')
    try:
        pairs = await process_uploaded_diamonds_csv(session, text_io, user_id)
    except (InvalidCSVFileError, TotalDiamondsLimitExceededError, DiamondsPerLoadLimitExceededError,
            NoActiveSubscriptionFoundError) as e:
        error_message = get_error_message(e)
        await handle_error_message(user_id, message, error_message)
        return
    else:
        unsuccessful_attempts[user_id] = 0
        await handle_successful_upload(message, pairs)


async def handle_error_message(user_id: int, message: types.Message, error_message: str):
    unsuccessful_attempts[user_id] += 1
    try:
        await message.answer(error_message)
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the error in the file.")
    else:
        logger.success("User was notified about the error")

    if unsuccessful_attempts[user_id] >= 2:
        await send_instructions_file(user_id, message)


async def send_instructions_file(user_id: int, message: types.Message):
    with open(INSTRUCTIONS_FILE_PATH, "rb") as file:
        file_content = file.read()

    instruction_file = BufferedInputFile(file_content, filename="Instructions.pdf")
    description = _("instructions_file_description")
    await message.answer_document(document=instruction_file, caption=description)
    unsuccessful_attempts[user_id] = 0


def get_error_message(exception: Exception) -> str:
    if isinstance(exception, InvalidCSVFileError):
        return _("Unable to process csv file.\n{errors}").format(errors="\n".join(exception.errors))
    elif isinstance(exception, TotalDiamondsLimitExceededError):
        return _("total_diamonds_limit_exceeded_error")
    elif isinstance(exception, DiamondsPerLoadLimitExceededError):
        return _("diamonds_per_load_limit_exceeded_error").format("1000")
    elif isinstance(exception, NoActiveSubscriptionFoundError):
        return _("no_active_subscription_found_error")
    return _("An unknown error occurred")


async def handle_successful_upload(message: types.Message, pairs: list):
    logger.info("CSV file processed successfully.")
    if len(pairs) == 0:
        try:
            await message.answer(_("csv_file_processed_successfully_without_pairs"))
        except TelegramBadRequest:
            logger.exception("Failed to notify user about the CSV file processed successfully without pairs")
        else:
            logger.success("User was notified about the CSV file processed successfully without pairs")
        finally:
            return
    pairs_csv_file_content = generate_csv_content(pairs)
    table_preview = generate_text_table(pairs)
    pairs_csv_file = BufferedInputFile(pairs_csv_file_content, filename="pairs.csv")
    try:
        await message.answer(_("list_of_pairs_preview").format(table_preview), parse_mode="markdown")
        await message.answer_document(
            document=pairs_csv_file,
            caption=_("csv_file_processed_successfully_with_pairs")
        )
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the CSV file processed successfully with pairs")
    else:
        logger.success("User was notified about the CSV file processed successfully with pairs")
