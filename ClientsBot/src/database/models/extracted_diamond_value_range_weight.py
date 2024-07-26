from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExtractedDiamondValueRangeWeight(Base):
    __tablename__ = 'extracted_diamond_value_range_weights'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    extracted_diamond_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('extracted_diamonds.id'), nullable=False)
    from_value: Mapped[float | None] = mapped_column(nullable=True)
    to_value: Mapped[float | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint('extracted_diamond_id', 'from_value', 'to_value'),
        CheckConstraint(
            'from_value IS NOT NULL OR to_value IS NOT NULL',
            name='check_from_or_to_value_not_null'
        ),
    )
