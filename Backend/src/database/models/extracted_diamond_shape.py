from sqlalchemy import ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Enum as SQLAlchemyEnum

from .base import Base
from .enums import Shape


class ExtractedDiamondShape(Base):
    __tablename__ = 'extracted_diamond_shapes'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    extracted_diamond_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('extracted_diamonds.id'), nullable=False)
    value: Mapped[Shape] = mapped_column(SQLAlchemyEnum(Shape), nullable=False)

    __table_args__ = (
        UniqueConstraint('extracted_diamond_id', 'value'),
    )
