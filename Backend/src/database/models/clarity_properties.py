from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLAlchemyEnum
from .base import Base
from .enums import Clarity


class ClarityProperties(Base):
    __tablename__ = 'clarity_properties'

    clarity: Mapped[Clarity] = mapped_column(SQLAlchemyEnum(Clarity), primary_key=True)
    index: Mapped[int] = mapped_column(nullable=False, unique=True)
    group: Mapped[int] = mapped_column(nullable=False)
