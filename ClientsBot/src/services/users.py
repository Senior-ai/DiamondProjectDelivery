from functools import lru_cache

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import User


async def add_user(
    session: AsyncSession,
    user: User,
) -> None:
    """Add a new user to the database."""
    user_id: int = user.id

    new_user = User(
        id=user_id,
        language_code=None
    )

    session.add(new_user)
    await session.commit()


@lru_cache
async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Checks if the user is in the database."""
    query = select(User.id).filter_by(id=user_id).limit(1)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return bool(user)


async def get_language_code(session: AsyncSession, user_id: int) -> str:
    query = select(User.language_code).filter_by(id=user_id)

    result = await session.execute(query)

    language_code = result.scalar_one_or_none()
    return language_code or ""


async def set_language_code(session: AsyncSession, user_id: int, language_code: str) -> None:
    stmt = update(User).where(User.id == user_id).values(language_code=language_code)

    await session.execute(stmt)
    await session.commit()
