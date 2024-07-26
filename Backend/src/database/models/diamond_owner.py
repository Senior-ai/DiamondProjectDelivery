from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import ForeignKey, UniqueConstraint, select, func, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import insert
from .base import Base


class DiamondOwner(Base):
    __tablename__ = 'diamond_owners'

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), primary_key=True)
    diamond_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('diamonds.id'), primary_key=True)
    upload_date: Mapped[datetime] = mapped_column()

    __table_args__ = (UniqueConstraint('user_id', 'diamond_id'),)

    @classmethod
    async def make_user(cls, session: AsyncSession, user_id: int, diamond_ids: list[int],
                        upload_date: datetime | None) -> None:
        if upload_date is None:
            upload_date = datetime.now()
        diamond_owners: list[dict[str, Any]] = []
        for diamond_id in diamond_ids:
            diamond_owner = {"user_id": user_id, "diamond_id": diamond_id, "upload_date": upload_date}
            logger.debug("DiamondOwner created: {}", diamond_owner)
            diamond_owners.append(diamond_owner)
        await session.execute(insert(cls)
                              .values(diamond_owners)
                              .on_conflict_do_nothing())
        await session.commit()

    @classmethod
    async def get_unique_owners(cls, session: AsyncSession, diamonds_ids: list[int]) -> list[int]:
        query = select(cls.user_id).filter(cls.diamond_id.in_(diamonds_ids)).group_by(cls.user_id)
        result = await session.execute(query)
        owners = list(result.scalars().all())
        return owners

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    @classmethod
    async def count_for_user(cls, session: AsyncSession, user_id: int) -> int:
        query = select(func.count(cls.diamond_id)).filter(cls.user_id == user_id)
        result = (await session.execute(query)).first()[0]
        return result

    def __repr__(self):
        return (f"<DiamondOwner(user_id={repr(self.user_id)}, diamond_id={repr(self.diamond_id)}, "
                f"upload_date={repr(self.upload_date)})>")
