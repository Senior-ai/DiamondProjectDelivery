from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import ForeignKey, select, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums.payment_purpose import PaymentPurpose


class GeneratedToken(Base):
    __tablename__ = 'generated_tokens'

    value: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    author_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    purpose: Mapped[PaymentPurpose] = mapped_column()

    @classmethod
    async def get_token_author(cls, session: AsyncSession, token_value: str) -> Optional[int]:
        query = select(cls.author_user_id).filter_by(value=token_value)

        result = await session.execute(query)

        author_user_id = result.scalar_one_or_none()
        return author_user_id

    @classmethod
    async def get(cls, session: AsyncSession, token_value: str) -> Optional["GeneratedToken"]:
        query = select(cls).filter_by(value=token_value)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def generate(cls, session: AsyncSession, author_user_id: int, purpose: PaymentPurpose) -> "GeneratedToken":
        generated_token = GeneratedToken(value=uuid4(), author_user_id=author_user_id, purpose=purpose)
        session.add(generated_token)
        await session.commit()
        return generated_token
