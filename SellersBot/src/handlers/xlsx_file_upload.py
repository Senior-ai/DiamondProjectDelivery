import io
from collections import defaultdict
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import dp, bot
from aiogram import types, F
from aiogram.types import ContentType
from aiogram.utils.i18n import gettext as _

from loguru import logger
import requests

unsuccessful_attempts = defaultdict(int)

@dp.message_handler(F.chat.type == ChatType.PRIVATE, F.content_type == ContentType.DOCUMENT)
async def xlsx_file_upload(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    logger.info("Received a document from user {}", user_id)

    if message.document.file_size > 1024 * 1024:
        await handle_error_message(user_id, message, _("file_too_large_error"))
        return

    if message.document.mime_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        logger.debug("Received file type {}", message.document.mime_type)
        await handle_error_message(user_id, message, _("invalid_file_type_error"))
        return

    stream = io.BytesIO()
    await bot.download(message.document, destination=stream)
    stream.seek(0)

    try:
        csv_data = await upload_xlsx_to_backend(stream, message.document.file_name)
        await handle_successful_upload(message, csv_data)
    except Exception as e:
        error_message = get_error_message(e)
        await handle_error_message(user_id, message, error_message)

async def upload_xlsx_to_backend(file_stream: io.BytesIO, filename: str) -> str:
    url = "http://backend_service/api/v1/upload_xlsx"  # TODO - Replace with actual URL
    files = {'file': (filename, file_stream, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    headers = {'Authorization': f'Bearer {'YOUR_ACCESS_TOKEN'}'}
    response = requests.post(url, files=files, headers=headers)

    if response.status_code != 200:
        raise Exception("Error processing file in backend")
    return response.text

async def handle_error_message(user_id: int, message: types.Message, error_message: str):
    unsuccessful_attempts[user_id] += 1
    try:
        await message.answer(error_message)
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the error in the file.")
    else:
        logger.success("User was notified about the error")

#     if unsuccessful_attempts[user_id] >= 2:
#         await send_instructions_file(user_id, message)

# async def send_instructions_file(user_id: int, message: types.Message):
#     with open(INSTRUCTIONS_FILE_PATH, "rb") as file:
#         file_content = file.read()

#     instruction_file = BufferedInputFile(file_content, filename="Instructions.pdf")
#     description = _("instructions_file_description")
#     await message.answer_document(document=instruction_file, caption=description)
#     unsuccessful_attempts[user_id] = 0

def get_error_message(exception: Exception) -> str:
    return _("An error occurred: {}").format(str(exception))

async def handle_successful_upload(message: types.Message, csv_data: str):
    logger.info("XLSX file processed successfully.")
    try:
        await message.answer(_("xlsx_file_processed_successfully"))
        # You can provide further handling of csv_data here if needed
    except TelegramBadRequest:
        logger.exception("Failed to notify user about the XLSX file processed successfully")
    else:
        logger.success("User was notified about the XLSX file processed successfully")
