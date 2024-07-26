from datetime import datetime

from loguru import logger
from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from .subscription_types import SubscriptionType
from .base import Base


class ActivatedSubscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    subscription_type_id: Mapped[int] = mapped_column(ForeignKey('subscription_types.id'))
    activation_date: Mapped[datetime] = mapped_column()

    @staticmethod
    async def create(session: AsyncSession, user_id: int,
                     subscription_type_id: int) -> "ActivatedSubscription":
        activation_date = datetime.now()
        subscription = ActivatedSubscription(user_id=user_id, subscription_type_id=subscription_type_id,
                                             activation_date=activation_date)
        session.add(subscription)
        await session.commit()
        return subscription

    @classmethod
    async def get_current_active_by_user_id(cls, session: AsyncSession, user_id: int) -> list["ActivatedSubscription"]:
        current_datetime = datetime.now()

        stmt = (
            select(ActivatedSubscription)
            .join(SubscriptionType, onclause=ActivatedSubscription.subscription_type_id == SubscriptionType.id)
            .where(ActivatedSubscription.user_id == user_id)
            .where(ActivatedSubscription.activation_date + SubscriptionType.duration >= current_datetime)
            .order_by(ActivatedSubscription.activation_date.desc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def deactivate_for_user(cls, session: AsyncSession, user_id: int) -> None:
        current_datetime = datetime.now()
        stmt = (
            select(ActivatedSubscription)
            .where(ActivatedSubscription.user_id == user_id)
            .where(ActivatedSubscription.activation_date + SubscriptionType.duration >= current_datetime)
        )
        result = await session.execute(stmt)
        subscriptions = result.scalars().all()
        for subscription in subscriptions:
            logger.info(f"Deactivating subscription {subscription.id}")
            await session.delete(subscription)
        await session.commit()
