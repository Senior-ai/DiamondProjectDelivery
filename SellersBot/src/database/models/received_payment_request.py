from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, BigInteger


class ReceivedPaymentRequests(Base):
    __tablename__ = 'received_payment_requests'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    request_datetime: Mapped[datetime] = mapped_column()
    request_json = Column(JSONB)

    @classmethod
    async def add(cls, session: AsyncSession, request_json: dict) -> "ReceivedPaymentRequests":
        received_payment_request = ReceivedPaymentRequests(request_datetime=datetime.now(), request_json=request_json)
        session.add(received_payment_request)
        await session.commit()
        return received_payment_request
