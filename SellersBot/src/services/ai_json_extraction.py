import asyncio
import json
from typing import Optional, Callable, Awaitable, Any

from ..database.models.processing_types import ExtractedDiamond
from ..core import openai_client
from ..core.config import JSON_EXTRACTOR_ASSISTANT_ID
from loguru import logger
from functools import wraps, lru_cache


class InvalidMessageType(Exception):
    pass


class FailedAttempt(Exception):
    pass


class InvalidRetryDecoratorArgument(Exception):
    pass


class Cacheable:
    def __init__(self, coroutine: Awaitable):
        self.coroutine = coroutine
        self.lock = asyncio.Lock()
        self.result: Any = None

    def __await__(self):
        return self._await_impl().__await__()

    async def _await_impl(self):
        async with self.lock:
            if self.result is None:
                self.result = await self.coroutine
            return self.result


def cacheable(function: Callable[..., Awaitable]):
    def wrapped(*args, **kwargs):
        r = function(*args, **kwargs)
        return Cacheable(r)

    return wrapped


def async_lru_cache(maxsize=128, typed=False):
    def decorator(fn):
        cache = lru_cache(maxsize=maxsize, typed=typed)(fn)

        async def wrapper(*args, **kwargs):
            return await cache(*args, **kwargs)

        return wrapper

    return decorator


def retry(attempts_limit: int = 3):
    if not isinstance(attempts_limit, int):
        raise InvalidRetryDecoratorArgument(f"Type int expected, {type(attempts_limit)} provided")

    if attempts_limit < 1:
        raise InvalidRetryDecoratorArgument(f"At least one attempt required for retry decorator to work. "
                                            f"{attempts_limit} attempts provided.")

    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            for attempt in range(attempts_limit):
                try:
                    return await function(*args, **kwargs)
                except FailedAttempt:
                    logger.warning("Failed attempt {}/{}", attempt + 1, attempts_limit)
            logger.warning("Function call failed after {} attempts", attempts_limit)
            raise FailedAttempt(f"Function call failed after {attempts_limit} attempts")

        return wrapper

    return decorator



@async_lru_cache(maxsize=128)
@cacheable
@retry()
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
    except IndexError:
        logger.exception("Failed JSON extraction attempt")
        raise FailedAttempt("Failed JSON extraction attempt")
    logger.success("Successfully extracted the raw diamonds list from the AI model response: {}", raw_diamonds_list)
    if raw_diamonds_list is None:
        return None

    diamonds_list = list(map(ExtractedDiamond.from_dict, raw_diamonds_list))
    logger.debug("Extracted diamonds list: {}", diamonds_list)
    return diamonds_list
