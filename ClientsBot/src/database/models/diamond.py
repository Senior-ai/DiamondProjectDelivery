from typing import Any

from loguru import logger
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLAlchemyEnum, UniqueConstraint, or_, union
from sqlalchemy.dialects.postgresql import insert

from .color_properties import ColorProperties
from .clarity_properties import ClarityProperties
from .base import Base
from sqlalchemy.future import select
from sqlalchemy import BigInteger

from .enums import Shape, Color, Clarity, Quality, Fluorescence, Culet
from .processing_types import ExtractedDiamond, ValueRange


class DiamondSearchError(Exception):
    pass


class DiamondAddError(Exception):
    pass


class Diamond(Base):
    __tablename__ = 'diamonds'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock: Mapped[str] = mapped_column(nullable=False)
    shape: Mapped[Shape] = mapped_column(SQLAlchemyEnum(Shape), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    color: Mapped[Color] = mapped_column(SQLAlchemyEnum(Color), nullable=False)
    clarity: Mapped[Clarity] = mapped_column(SQLAlchemyEnum(Clarity), nullable=False)
    lab: Mapped[str] = mapped_column(nullable=False)
    certificate_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    length: Mapped[float] = mapped_column(nullable=False)
    width: Mapped[float] = mapped_column(nullable=False)
    depth: Mapped[float] = mapped_column(nullable=False)
    ratio: Mapped[float] = mapped_column(nullable=False)
    cut: Mapped[Quality] = mapped_column(SQLAlchemyEnum(Quality), nullable=False)
    polish: Mapped[Quality] = mapped_column(SQLAlchemyEnum(Quality), nullable=False)
    symmetry: Mapped[Quality] = mapped_column(SQLAlchemyEnum(Quality), nullable=False)
    fluorescence: Mapped[Fluorescence] = mapped_column(SQLAlchemyEnum(Fluorescence), nullable=False)
    table: Mapped[float] = mapped_column(nullable=False)
    depth_percentage: Mapped[float] = mapped_column(nullable=False)
    gridle: Mapped[str] = mapped_column(nullable=False)
    culet: Mapped[Culet] = mapped_column(SQLAlchemyEnum(Culet), nullable=False)
    certificate_comment: Mapped[str] = mapped_column(nullable=True)
    rapnet: Mapped[int] = mapped_column(BigInteger, nullable=True)
    price_per_carat: Mapped[int] = mapped_column(BigInteger, nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)

    __table_args__ = (UniqueConstraint('stock', 'shape', 'weight', 'color', 'clarity', 'lab',
                                       'certificate_number', 'length', 'width', 'depth', 'ratio', 'cut', 'polish',
                                       'symmetry', 'fluorescence', 'table', 'depth_percentage', 'gridle', 'culet'),)

    @staticmethod
    async def add_diamonds(session: AsyncSession, diamonds: list[dict[str, Any]]) -> list[int]:
        if any(not isinstance(diamond, dict) for diamond in diamonds):
            raise ValueError(
                "All elements of diamonds should be of type dict with keys matching the Diamond model fields.")

        inserted_ids = []

        for diamond in diamonds:
            stmt = (
                insert(Diamond)
                .values(diamond)
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    'stock', 'shape', 'weight', 'color', 'clarity', 'lab',
                    'certificate_number', 'length', 'width', 'depth', 'ratio', 'cut', 'polish',
                    'symmetry', 'fluorescence', 'table', 'depth_percentage', 'gridle', 'culet'
                ],
                set_={
                    'certificate_comment': stmt.excluded.certificate_comment,
                    'rapnet': stmt.excluded.rapnet,
                    'price_per_carat': stmt.excluded.price_per_carat,
                    'picture': stmt.excluded.picture
                }
            ).returning(Diamond.id)

            try:
                result = await session.execute(stmt)
                diamond_id = result.scalar()
                if diamond_id:
                    inserted_ids.append(diamond_id)
            except IntegrityError:
                # Skip this diamond if there's a conflict or any other IntegrityError
                continue

        await session.commit()

        return inserted_ids

    def __repr__(self):
        return f"<Diamond(stock={repr(self.stock)}, shape={repr(self.shape)}, weight={repr(self.weight)}, color={repr(self.color)}, " \
               f"clarity={repr(self.clarity)}, lab={repr(self.lab)}, certificate_number={repr(self.certificate_number)}, " \
               f"length={repr(self.length)}, width={repr(self.width)}, depth={repr(self.depth)}, ratio={repr(self.ratio)}, " \
               f"cut={repr(self.cut)}, polish={repr(self.polish)}, symmetry={repr(self.symmetry)}, fluorescence={repr(self.fluorescence)}, " \
               f"table={repr(self.table)}, depth_percentage={repr(self.depth_percentage)}, gridle={repr(self.gridle)}, culet={repr(self.culet)}, " \
               f"certificate_comment={repr(self.certificate_comment)}, rapnet={repr(self.rapnet)}, price_per_carat={repr(self.price_per_carat)}, " \
               f"picture={repr(self.picture)})>"

    @property
    def as_dict(self) -> dict[str, Any]:
        return {
            'stock': self.stock,
            'shape': self.shape,
            'weight': self.weight,
            'color': self.color,
            'clarity': self.clarity,
            'lab': self.lab,
            'certificate_number': self.certificate_number,
            'length': self.length,
            'width': self.width,
            'depth': self.depth,
            'ratio': self.ratio,
            'cut': self.cut,
            'polish': self.polish,
            'symmetry': self.symmetry,
            'fluorescence': self.fluorescence,
            'table': self.table,
            'depth_percentage': self.depth_percentage,
            'gridle': self.gridle,
            'culet': self.culet,
            'certificate_comment': self.certificate_comment,
            'rapnet': self.rapnet,
            'price_per_carat': self.price_per_carat,
            'picture': self.picture
        }

    @classmethod
    async def get_all_diamonds(cls, session: AsyncSession) -> list["Diamond"]:
        stmt = select(Diamond)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def find_similar_diamonds_ids(cls, session: AsyncSession, extracted_diamonds: list[ExtractedDiamond]) -> list[int]:
        if not isinstance(session, AsyncSession):
            logger.error(f"Session must be an instance of AsyncSession, got {type(session)}")
            raise ValueError("Session must be an instance of AsyncSession.")
        if any(not isinstance(diamond, ExtractedDiamond) for diamond in extracted_diamonds):
            logger.error(f"All elements of extracted_diamonds must be of type ExtractedDiamond.")
            raise ValueError("All elements of extracted_diamonds must be of type ExtractedDiamond.")
        if len(extracted_diamonds) == 0:
            return []

        queries = []

        for diamond in extracted_diamonds:
            current_stmt = (select(Diamond.id)
                            .join(ColorProperties, Diamond.color == ColorProperties.color)
                            .join(ClarityProperties, Diamond.clarity == ClarityProperties.clarity))
            logger.debug("Initial statement: {}", current_stmt)
            match diamond.color:
                case Color() as color:
                    logger.debug("Matched literal: {}", color)
                    color_subquery = select(ColorProperties.index, ColorProperties.group).where(
                        ColorProperties.color == color).limit(1).subquery()
                    current_stmt = current_stmt.filter(
                        ColorProperties.index.between(color_subquery.c.index - 1, color_subquery.c.index + 1))
                    current_stmt = current_stmt.filter(ColorProperties.group == color_subquery.c.group)
                    logger.debug("Statement after filtering color: {}", current_stmt)
                case list() as colors:
                    logger.debug("Matched list: {}", colors)
                    filter_units = []
                    for color in colors:
                        match color:
                            case Color():
                                logger.debug("Matched color: {}", color)
                                color_subquery = select(ColorProperties.index, ColorProperties.group).where(
                                    ColorProperties.color == color).limit(1).subquery()
                                current_stmt = current_stmt.filter(
                                    ColorProperties.index.between(color_subquery.c.index - 1,
                                                                  color_subquery.c.index + 1))
                                filter_units.append(ColorProperties.index.between(color_subquery.c.index - 1,
                                                                                  color_subquery.c.index + 1))
                                filter_units.append(ColorProperties.group == color_subquery.c.group)
                            case ValueRange(from_value=Color() | None as from_value,
                                            to_value=Color() | None as to_value):
                                logger.debug("Matched range: {} to {}", from_value, to_value)
                                from_subquery = select(ColorProperties.index, ColorProperties.group).where(
                                    ColorProperties.color == from_value).limit(1).subquery()
                                to_subquery = select(ColorProperties.index, ColorProperties.group).where(
                                    ColorProperties.color == to_value).limit(1).subquery()
                                filter_units.append(ColorProperties.index.between(from_subquery.c.index - 1,
                                                                                    to_subquery.c.index + 1))
                                filter_units.append(ColorProperties.group == from_subquery.c.group)
                    current_stmt = current_stmt.filter(or_(*filter_units))
                    logger.debug("Statement after filtering color: {}", current_stmt)
                case ValueRange(from_value=Color() as from_color, to_value=Color() as to_color):
                    logger.debug("Matched range: {} to {}", from_color, to_color)
                    from_subquery = select(ColorProperties.index, ColorProperties.group).where(
                        ColorProperties.color == from_color).limit(1).subquery()
                    to_subquery = select(ColorProperties.index, ColorProperties.group).where(
                        ColorProperties.color == to_color).limit(1).subquery()
                    current_stmt = current_stmt.filter(ColorProperties.index.between(from_subquery.c.index,
                                                                                        to_subquery.c.index))
                    current_stmt = current_stmt.filter(ColorProperties.group == from_subquery.c.group)
                    logger.debug("Statement after filtering color: {}", current_stmt)
                case None:
                    logger.debug("Matched color None")
                case _:
                    logger.error("Matched unknown color: {}", diamond.color)

            match diamond.clarity:
                case Clarity() as clarity:
                    logger.debug("Matched enum: {}", clarity)
                    clarity_subquery = select(ClarityProperties.index, ClarityProperties.group).where(
                        ClarityProperties.clarity == clarity).limit(1).subquery()
                    current_stmt = current_stmt.filter(
                        ClarityProperties.index.between(clarity_subquery.c.index - 1, clarity_subquery.c.index + 1))
                    current_stmt = current_stmt.filter(ClarityProperties.group == clarity_subquery.c.group)
                    logger.debug("Statement after filtering clarity: {}", current_stmt)
                case list() as clarities:
                    logger.debug("Matched list: {}", clarities)
                    filter_units = []
                    for clarity in clarities:
                        match clarity:
                            case Clarity():
                                logger.debug("Matched clarity: {}", clarity)
                                clarity_subquery = select(ClarityProperties.index, ClarityProperties.group).where(
                                    ClarityProperties.clarity == clarity).limit(1).subquery()
                                current_stmt = current_stmt.filter(
                                    ClarityProperties.index.between(clarity_subquery.c.index - 1,
                                                                   clarity_subquery.c.index + 1))
                                filter_units.append(ClarityProperties.index.between(clarity_subquery.c.index - 1,
                                                                                   clarity_subquery.c.index + 1))
                                filter_units.append(ClarityProperties.group == clarity_subquery.c.group)
                                logger.debug("Statement after filtering clarity: {}", current_stmt)
                            case ValueRange(from_value=Clarity() | None as from_value,
                                            to_value=Clarity() | None as to_value):
                                logger.debug("Matched range: {} to {}", from_value, to_value)
                                from_subquery = select(ClarityProperties.index, ClarityProperties.group).where(
                                    ClarityProperties.clarity == from_value).limit(1).subquery()
                                to_subquery = select(ClarityProperties.index, ClarityProperties.group).where(
                                    ClarityProperties.clarity == to_value).limit(1).subquery()
                                filter_units.append(ClarityProperties.index.between(from_subquery.c.index,
                                                                                      to_subquery.c.index))
                                filter_units.append(ClarityProperties.group == from_subquery.c.group)
                                logger.debug("Statement after filtering clarity: {}", current_stmt)
                    current_stmt = current_stmt.filter(or_(*filter_units))
                    logger.debug("Statement after filtering clarity: {}", current_stmt)
                case ValueRange(from_value=Clarity() | None as from_clarity, to_value=Clarity() | None as to_clarity):
                    logger.debug("Matched single range: {} to {}", from_clarity, to_clarity)
                    from_subquery = select(ClarityProperties.index, ClarityProperties.group).where(
                        ClarityProperties.clarity == from_clarity).limit(1).subquery()
                    to_subquery = select(ClarityProperties.index, ClarityProperties.group).where(
                        ClarityProperties.clarity == to_clarity).limit(1).subquery()
                    current_stmt = current_stmt.filter(ClarityProperties.index.between(from_subquery.c.index,
                                                                                        to_subquery.c.index))
                    current_stmt = current_stmt.filter(ClarityProperties.group == from_subquery.c.group)
                    logger.debug("Statement after filtering clarity: {}", current_stmt)
                case None:
                    logger.debug("Matched clarity None")
                case _:
                    logger.error("Matched unknown clarity: {}", diamond.clarity)

            match diamond.carat:
                case float() | int() as carat:
                    logger.debug("Matched float: {}", carat)
                    current_stmt = current_stmt.filter(Diamond.weight.between(carat - 0.15, carat + 0.15))
                    logger.debug("Statement after filtering carats: {}", current_stmt)
                case list() as carats:
                    logger.debug("Matched list: {}", carats)
                    filter_units = []
                    for carat in carats:
                        match carat:
                            case float() | int():
                                logger.debug("Matched carat: {}", carat)
                                filter_units.append(Diamond.weight.between(carat - 0.15, carat + 0.15))
                            case ValueRange(from_value=float() | int() | None as from_value,
                                            to_value=float() | int() | None as to_value):
                                logger.debug("Matched range: {} to {}", from_value, to_value)
                                filter_units.append(Diamond.weight.between(from_value, to_value))
                    current_stmt = current_stmt.filter(or_(*filter_units))
                    logger.debug("Statement after filtering carats: {}", current_stmt)
                case ValueRange(from_value=float() | int() as from_carat, to_value=float() | int() as to_carat):
                    logger.debug("Matched range: {} to {}", from_carat, to_carat)
                    current_stmt = current_stmt.filter(Diamond.weight.between(from_carat, to_carat))
                    logger.debug("Statement after filtering carats: {}", current_stmt)
                case None:
                    logger.debug("Matched carat None")
                case _:
                    logger.error("Matched unknown carats: {}", diamond.carat)

            match diamond.shape:
                case Shape() as shape:
                    logger.debug("Matched shape: {}", shape)
                    current_stmt = current_stmt.filter(Diamond.shape == shape)
                    logger.debug("Statement after filtering shape: {}", current_stmt)
                case list() as shapes:
                    logger.debug("Matched list: {}", shapes)
                    filter_units = []
                    for shape in shapes:
                        match shape:
                            case Shape():
                                filter_units.append(Diamond.shape == shape)
                            case ValueRange(from_value=Shape() | None as from_value, to_value=Shape() | None as to_value):
                                possible_shapes = []
                                if from_value is not None:
                                    possible_shapes.append(from_value)
                                if to_value is not None:
                                    possible_shapes.append(to_value)
                                filter_units.append(Diamond.shape.in_(possible_shapes))
                    current_stmt = current_stmt.filter(or_(*filter_units))
                    logger.debug("Statement after filtering shape: {}", current_stmt)
                case ValueRange(from_value=Shape() | None as from_shape, to_value=Shape() | None as to_shape):
                    logger.debug("Matched range: {} to {}", from_shape, to_shape)
                    possible_shapes = []
                    if from_shape is not None:
                        possible_shapes.append(from_shape)
                    if to_shape is not None:
                        possible_shapes.append(to_shape)
                    current_stmt = current_stmt.filter(Diamond.shape.in_(possible_shapes))
                    logger.debug("Statement after filtering shape: {}", current_stmt)
                case None:
                    logger.debug("Matched shape None")
                case _:
                    logger.error("Matched unknown shape: {}", diamond.shape)

            queries.append(current_stmt)

        stmt = union(*queries)

        logger.debug("Final statement: {}", stmt)

        try:
            result = await session.execute(stmt)
        except DBAPIError:
            logger.exception("Error executing statement.")
            raise DiamondSearchError("Error executing statement.")
        return list(result.scalars().all())

    @classmethod
    async def find_pairs_for_list(cls, session: AsyncSession, diamonds_ids: list[int]) -> list["Diamond"]:
        # weight_similar_diamonds = select(Diamond)
        stmt = select(Diamond).filter(Diamond.id.in_(diamonds_ids))
        result = await session.execute(stmt)
        return list(result.scalars().all())
