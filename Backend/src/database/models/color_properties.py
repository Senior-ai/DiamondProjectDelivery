from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLAlchemyEnum
from .base import Base
from .enums import Color


class ColorProperties(Base):
    __tablename__ = 'colors_properties'

    color: Mapped[Color] = mapped_column(SQLAlchemyEnum(Color), primary_key=True)
    index: Mapped[int] = mapped_column(nullable=False, unique=True)
    group: Mapped[int] = mapped_column(nullable=False)
