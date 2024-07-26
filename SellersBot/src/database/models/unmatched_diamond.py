from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UnmatchedDiamond(Base):
    __tablename__ = 'unmatched_diamonds'

    extracted_diamond_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("extracted_diamonds.id"), primary_key=True)
    queried_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
