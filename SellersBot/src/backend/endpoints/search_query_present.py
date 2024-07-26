from ..models.search_query import SearchQuery
from ..models.search_query_notification_status import SearchQueryNotificationStatus
from ...database.loader import sessionmaker
from loguru import logger
from ..router import router
from ...services.process_search_query import (
    process_search_query,
    SellersNotificationError,
    NotEnoughDataAboutDiamondsException,
    NoDiamondsInMessage,
)


@router.post('/search_query_present/', response_model=SearchQueryNotificationStatus)
async def search_query_present(query: SearchQuery) -> SearchQueryNotificationStatus:
    logger.info("Received search query from user_id: {}", query.user_id)

    async with sessionmaker() as session:
        try:
            notified_sellers_amount = await process_search_query(session, query.message, query.user_id,
                                                                 free_notification=False)
        except NoDiamondsInMessage:
            logger.info("No diamonds in the client's message found")
            return SearchQueryNotificationStatus(message="No diamonds found", data=None)
        except NotEnoughDataAboutDiamondsException:
            logger.info("Not enough data about diamonds in the client's message")
            return SearchQueryNotificationStatus(message="Not enough data about diamonds", data=None)
        except SellersNotificationError:
            logger.exception("Failed to notify sellers. This must never happen!")
            return SearchQueryNotificationStatus(message="Failed to notify sellers", data=None)

    logger.info("Successfully notified {} sellers.", notified_sellers_amount)

    return SearchQueryNotificationStatus(message="Notified sellers", data=notified_sellers_amount)
