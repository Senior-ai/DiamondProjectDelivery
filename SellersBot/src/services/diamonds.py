from sqlalchemy import delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import DiamondOwner, Diamond


async def is_user_owns_diamond(session: AsyncSession, user_id: int, stock: str) -> bool:
    """Check if the user owns the stone."""
    query = (
        select(DiamondOwner)
        .join(Diamond)
        .where(
            and_(
                DiamondOwner.user_id == user_id,
                Diamond.stock == stock
            )
        )
    )

    result = await session.execute(query)
    diamond_owner = result.scalar_one_or_none()
    return diamond_owner is not None


async def delete_diamond_for_user(session: AsyncSession, user_id: int, stock: str) -> None:
    """Delete the stone from the user's stock."""
    diamonds_to_delete = (
        select(DiamondOwner.diamond_id)
        .join(Diamond)
        .where(
            and_(
                DiamondOwner.user_id == user_id,
                Diamond.stock == stock
            )
        )
    )
    query = (
        delete(DiamondOwner)
        .where(
            and_(
                DiamondOwner.diamond_id.in_(diamonds_to_delete),
                DiamondOwner.user_id == user_id
            )
        )
    )

    await session.execute(query)
    await session.commit()
