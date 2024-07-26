from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.models import Diamond, DiamondOwner


async def get_diamond_lists_grouped_by_sellers(session: AsyncSession, similar_diamonds_ids: list[int]) \
        -> dict[int, list[Diamond]]:
    query = (
        select(DiamondOwner.user_id, Diamond)
        .join(Diamond)
        .filter(Diamond.id.in_(similar_diamonds_ids))
    )
    result = await session.execute(query)
    diamond_lists: defaultdict[int, list[Diamond]] = defaultdict(list)
    for user_id, diamond in result:
        diamond_lists[user_id].append(diamond)
    return dict(diamond_lists)
