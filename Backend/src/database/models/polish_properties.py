from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Enum as SQLAlchemyEnum
from .base import Base
from .enums import Quality


class PolishProperties(Base):
    __tablename__ = 'polish_properties'

    polish: Mapped[Quality] = mapped_column(SQLAlchemyEnum(Quality), primary_key=True)
    index: Mapped[int] = mapped_column(nullable=False, unique=True)
