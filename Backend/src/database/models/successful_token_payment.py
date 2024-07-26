from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SuccessfulTokenPayment(Base):
    __tablename__ = 'successful_token_payments'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    payment_request_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('received_payment_requests.id'))
    token: Mapped[str] = mapped_column(ForeignKey('generated_tokens.value'))
    usd_amount: Mapped[float] = mapped_column()

    @staticmethod
    async def create(session: AsyncSession, payment_request_id: int, token_value: str, usd_amount: float) -> "SuccessfulTokenPayment":
        payment = SuccessfulTokenPayment(payment_request_id=payment_request_id, token=token_value,
                                         usd_amount=usd_amount)
        session.add(payment)
        await session.commit()
        return payment
