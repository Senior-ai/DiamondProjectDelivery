from datetime import timedelta
from sqlalchemy.future import select

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class SubscriptionType(Base):
    __tablename__ = 'subscription_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    duration: Mapped[timedelta] = mapped_column()
    max_diamonds_per_load: Mapped[int] = mapped_column()
    total_new_diamonds_per_period: Mapped[int] = mapped_column()

    __table_args__ = (UniqueConstraint('name', 'duration', 'max_diamonds_per_load',
                                       'total_new_diamonds_per_period'),)

    @classmethod
    async def get_by_name(cls, session, name: str) -> "SubscriptionType":
        stmt = select(cls).where(cls.name == name)
        result = await session.execute(stmt)
        return result.scalars().first()
