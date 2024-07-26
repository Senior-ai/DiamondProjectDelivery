from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums import Quality


class CutProperties(Base):
    __tablename__ = 'cut_properties'

    cut: Mapped[Quality] = mapped_column(SQLAlchemyEnum(Quality), primary_key=True)
    index: Mapped[int] = mapped_column(nullable=False, unique=True)
