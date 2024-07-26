from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLAlchemyEnum

from .base import Base
from .enums import Color


class ExtractedDiamondValueRangeColor(Base):
    __tablename__ = 'extracted_diamond_value_range_colors'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    extracted_diamond_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('extracted_diamonds.id'), nullable=False)
    from_value: Mapped[Color | None] = mapped_column(SQLAlchemyEnum(Color), nullable=True)
    to_value: Mapped[Color | None] = mapped_column(SQLAlchemyEnum(Color), nullable=True)

    __table_args__ = (
        UniqueConstraint('extracted_diamond_id', 'from_value', 'to_value'),
        CheckConstraint(
            'from_value IS NOT NULL OR to_value IS NOT NULL',
            name='check_from_or_to_value_not_null'
        ),
    )
