from sqlalchemy.ext.asyncio import AsyncSession

from .save_extracted_diamonds_as_unmatched import save_extracted_diamonds_as_unmatched
from ..database.models import Diamond
from .ai_json_extraction import extract_diamonds_from_message_with_ai, FailedAttempt
from .diamond_filtering import filter_incomplete_diamonds
from .diamond_grouping import get_diamond_lists_grouped_by_sellers
from .notification import notify_diamonds_owner


class SellersNotificationError(Exception):
    pass


class NotEnoughDataAboutDiamondsException(Exception):
    pass


class NoDiamondsInMessage(Exception):
    pass


async def process_search_query(session: AsyncSession, message_text: str, interested_user_id: int,
                               free_notification: bool = False) -> int:
    try:
        diamonds = await extract_diamonds_from_message_with_ai(message_text)
    except FailedAttempt:
        raise SellersNotificationError
    if not diamonds:
        raise NoDiamondsInMessage

    diamonds = filter_incomplete_diamonds(diamonds)
    if not diamonds:
        raise NotEnoughDataAboutDiamondsException

    similar_diamonds_ids = await Diamond.find_similar_diamonds_ids(session, diamonds)
    diamonds_by_sellers = await get_diamond_lists_grouped_by_sellers(session, similar_diamonds_ids)

    if not diamonds_by_sellers:
        await save_extracted_diamonds_as_unmatched(session, diamonds, interested_user_id)
        return 0

    return await notify_diamonds_owner(session, interested_user_id, diamonds_by_sellers, diamonds, free_notification)
