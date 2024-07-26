from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List, Optional, Protocol, Any
from functools import partial

from ..database.models import (
    ExtractedDiamond as ExtractedDiamondORM,
    UnmatchedDiamond,
    ExtractedDiamondWeight,
    ExtractedDiamondValueRangeWeight,
    ExtractedDiamondColor,
    ExtractedDiamondValueRangeColor,
    ExtractedDiamondClarity,
    ExtractedDiamondValueRangeClarity,
    ExtractedDiamondShape,
    ExtractedDiamondValueRangeShape
)
from ..database.models.processing_types import ExtractedDiamond as ExtractedDiamondProcessingType
from ..database.models.processing_types import ValueRange


async def save_extracted_diamonds_as_unmatched(
        session: AsyncSession, diamonds: List[ExtractedDiamondProcessingType], queried_user_id: int) -> None:
    """Save extracted diamonds as unmatched."""

    saving_time = datetime.now()

    # Pre-create the partial functions for saving different attributes
    save_diamond_weight = partial(save_diamond_attribute, single_value_model=ExtractedDiamondWeight,
                                  value_range_model=ExtractedDiamondValueRangeWeight)
    save_diamond_color = partial(save_diamond_attribute, single_value_model=ExtractedDiamondColor,
                                 value_range_model=ExtractedDiamondValueRangeColor)
    save_diamond_clarity = partial(save_diamond_attribute, single_value_model=ExtractedDiamondClarity,
                                   value_range_model=ExtractedDiamondValueRangeClarity)
    save_diamond_shape = partial(save_diamond_attribute, single_value_model=ExtractedDiamondShape,
                                 value_range_model=ExtractedDiamondValueRangeShape)

    for diamond in diamonds:
        # Create and save the ExtractedDiamondORM instance
        extracted_diamond = ExtractedDiamondORM(extraction_date=saving_time)
        session.add(extracted_diamond)
        await session.flush()  # Ensure the ID is generated

        # Create an UnmatchedDiamond entry
        unmatched_diamond = UnmatchedDiamond(
            extracted_diamond_id=extracted_diamond.id,
            queried_user_id=queried_user_id
        )
        session.add(unmatched_diamond)

        # Save diamond attributes (weight, color, clarity, shape)
        await save_diamond_weight(session, extracted_diamond.id, diamond.carat)
        await save_diamond_color(session, extracted_diamond.id, diamond.color)
        await save_diamond_clarity(session, extracted_diamond.id, diamond.clarity)
        await save_diamond_shape(session, extracted_diamond.id, diamond.shape)

    await session.commit()


class SingleValueModel[T](Protocol):
    extracted_diamond_id: int
    value: Optional[T]

    def __call__(self,
                 extracted_diamond_id: int,
                 value: Optional[T],
                 *args, **kwargs) -> Any:
        ...


class ValueRangeModel[T](Protocol):
    extracted_diamond_id: int
    from_value: Optional[T]
    to_value: Optional[T]

    def __call__(self,
                 extracted_diamond_id: int,
                 from_value: Optional[T],
                 to_value: Optional[T],
                 *args, **kwargs) -> Any:
        ...


async def save_diamond_attribute[T](
        session: AsyncSession, extracted_diamond_id: int,
        attribute: Union[Optional[T], ValueRange[T], List[Union[Optional[T], ValueRange[T]]]],
        single_value_model: SingleValueModel[T], value_range_model: ValueRangeModel[T]
) -> None:
    match attribute:
        case list():
            for item in attribute:
                await save_diamond_attribute(session, extracted_diamond_id, item, single_value_model, value_range_model)
        case ValueRange() as value_range if value_range.is_valid():
            value_range_entry = value_range_model(
                extracted_diamond_id=extracted_diamond_id,
                from_value=value_range.from_value,
                to_value=value_range.to_value
            )
            session.add(value_range_entry)
        case None:
            pass
        case _:
            single_value_entry = single_value_model(
                extracted_diamond_id=extracted_diamond_id,
                value=attribute
            )
            session.add(single_value_entry)
