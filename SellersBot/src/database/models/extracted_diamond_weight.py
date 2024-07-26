from sqlalchemy import ForeignKey, Integer, UniqueConstraint, BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class ExtractedDiamondWeight(Base):
    __tablename__ = 'extracted_diamond_weights'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    extracted_diamond_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('extracted_diamonds.id'), nullable=False)
    value: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint('extracted_diamond_id', 'value'),
    )
