import json
from typing import Optional

from ..database.models.processing_types import ExtractedDiamond
from ..core import openai_client
from ..core.config import JSON_EXTRACTOR_ASSISTANT_ID
from loguru import logger


class InvalidMessageType(Exception):
    pass


async def extract_diamonds_from_message_with_ai(message: str) -> Optional[list[ExtractedDiamond]]:
    if not isinstance(message, str):
        raise InvalidMessageType("Message must be a string")

    logger.info("Creating a new thread for JSON extraction AI model")
    thread = await openai_client.beta.threads.create()

    logger.info("Sending a message to the AI model")
    await openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )

    logger.info("Running the AI model")
    run = await openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=JSON_EXTRACTOR_ASSISTANT_ID,
    )

    logger.info("Getting the messages from the AI model")
    messages = await openai_client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)

    logger.info("Extracting the diamonds from the AI model response")
    try:
        raw_diamonds_list = json.loads(messages.data[0].content[0].text.value).get("diamonds")
    except json.JSONDecodeError:
        logger.error("Error while decoding the JSON response. This must never happen!")
        return None
    logger.success("Successfully extracted the raw diamonds list from the AI model response: {}", raw_diamonds_list)
    if raw_diamonds_list is None:
        return None

    diamonds_list = list(map(ExtractedDiamond.from_dict, raw_diamonds_list))
    logger.debug("Extracted diamonds list: {}", diamonds_list)
    return diamonds_list
