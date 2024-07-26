from sqlalchemy.future import select

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums import PaymentPurpose


class PaymentPurposePrice(Base):
    __tablename__ = "payment_purpose_prices"

    purpose: Mapped[PaymentPurpose] = mapped_column(primary_key=True)
    usd_price: Mapped[float] = mapped_column()

    @classmethod
    async def get(cls, session, purpose: PaymentPurpose) -> float:
        stmt = select(cls).where(cls.purpose == purpose)
        result = await session.execute(stmt)
        return result.scalars().first().usd_price
