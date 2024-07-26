from sqlalchemy.ext.asyncio import AsyncSession

from .values import values


async def add_all_defaults(session: AsyncSession):
    session.add_all(values)
    await session.commit()
