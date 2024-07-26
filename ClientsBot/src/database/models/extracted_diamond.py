from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExtractedDiamond(Base):
    __tablename__ = 'extracted_diamonds'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    extraction_date: Mapped[datetime] = mapped_column(nullable=False)
