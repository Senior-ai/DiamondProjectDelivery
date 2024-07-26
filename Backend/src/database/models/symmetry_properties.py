from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Enum as SQLAlchemyEnum
from .base import Base
from .enums import Quality


class SymmetryProperties(Base):
    __tablename__ = 'symetry_properties'

    symmetry: Mapped[Quality] = mapped_column(SQLAlchemyEnum(Quality), primary_key=True)
    index: Mapped[int] = mapped_column(nullable=False, unique=True)
