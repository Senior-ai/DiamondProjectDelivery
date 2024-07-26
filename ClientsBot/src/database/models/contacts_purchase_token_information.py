from typing import Union
from uuid import UUID

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ContactsPurchaseTokenInformation(Base):
    __tablename__ = 'contacts_purchase_token_information'

    token: Mapped[UUID] = mapped_column(ForeignKey('generated_tokens.value'), primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<ContactsPurchaseInformation(token={repr(self.token)}, client_id={repr(self.client_id)})>"

    @classmethod
    async def add(cls, session: AsyncSession, token: UUID, client_id: int) -> None:
        record = cls(token=token, client_id=client_id)
        session.add(record)
        await session.commit()

    @classmethod
    async def get(cls, session: AsyncSession, token: UUID) -> Union["ContactsPurchaseTokenInformation", None]:
        return await session.get(cls, token)
