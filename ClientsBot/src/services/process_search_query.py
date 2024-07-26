import aiohttp
from aiohttp import ServerDisconnectedError
from loguru import logger

from ..core.config import SELLERS_BOT_BACKEND_URL

type NotifiedSellersAmount = int


class SellersNotificationError(Exception):
    pass


class NotEnoughDataAboutDiamondsException(Exception):
    pass


async def process_search_query(message_text: str,
                               client_id: int) -> NotifiedSellersAmount | None:
    async with aiohttp.ClientSession() as http_session:
        try:
            async with http_session.post(f"{SELLERS_BOT_BACKEND_URL}/api/v1/search_query_present/",
                                         json={"user_id": client_id, "message": message_text}) as response:
                if response.status != 200:
                    logger.error("Failed to notify sellers. Status code: {}", response.status)
                    raise SellersNotificationError("Failed to notify sellers")

                response_data = await response.json()
                message = response_data.get("message", "")
                data = response_data.get("data", None)

                if message == "No diamonds found":
                    logger.info("No diamonds found in the message.")
                    return None
                elif message == "Not enough data about diamonds":
                    raise NotEnoughDataAboutDiamondsException("Not enough data about diamonds")
                elif message == "No sellers to notify":
                    logger.info("No sellers to notify.")
                    return 0
                elif message == "Notified sellers":
                    successfully_notified_sellers_amount = int(data)
                    logger.success("Notified {} sellers.", successfully_notified_sellers_amount)
                    return successfully_notified_sellers_amount
                else:
                    logger.error("Unexpected response message: {}", message)
                    raise SellersNotificationError("Failed to notify sellers")
        except ServerDisconnectedError:
            logger.exception("Failed to notify sellers. Server disconnected")
            raise SellersNotificationError("Failed to notify sellers")
