from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
from sqlalchemy.orm import aliased

from ..database.models import (
    Diamond, ColorProperties, ClarityProperties, CutProperties, PolishProperties, SymmetryProperties,
    DiamondOwner
)
from loguru import logger


async def find_pairs_for_diamonds(session: AsyncSession, diamonds_ids: list[int]) -> list[Diamond]:
    initial_diamond = aliased(Diamond)
    pair_diamond = aliased(Diamond)

    initial_diamond_color = aliased(ColorProperties)
    initial_diamond_clarity = aliased(ClarityProperties)
    initial_diamond_cut = aliased(CutProperties)
    initial_diamond_polish = aliased(PolishProperties)
    initial_diamond_symmetry = aliased(SymmetryProperties)
    initial_diamond_owner = aliased(DiamondOwner)

    pair_diamond_color = aliased(ColorProperties)
    pair_diamond_clarity = aliased(ClarityProperties)
    pair_diamond_cut = aliased(CutProperties)
    pair_diamond_polish = aliased(PolishProperties)
    pair_diamond_symmetry = aliased(SymmetryProperties)

    pair_diamond_owner = aliased(DiamondOwner)

    query = (
        select(pair_diamond)
        .select_from(initial_diamond)
        # Join the initial diamond properties
        .join(initial_diamond_color, initial_diamond.color == initial_diamond_color.color)
        .join(initial_diamond_clarity, initial_diamond.clarity == initial_diamond_clarity.clarity)
        .join(initial_diamond_cut, initial_diamond.cut == initial_diamond_cut.cut)
        .join(initial_diamond_polish, initial_diamond.polish == initial_diamond_polish.polish)
        .join(initial_diamond_symmetry, initial_diamond.symmetry == initial_diamond_symmetry.symmetry)
        .join(initial_diamond_owner, initial_diamond.id == initial_diamond_owner.diamond_id)
        # Join the pair diamond
        .join(pair_diamond, pair_diamond.id != initial_diamond.id)
        # Join the pair diamond properties
        .join(pair_diamond_color, pair_diamond.color == pair_diamond_color.color)
        .join(pair_diamond_clarity, pair_diamond.clarity == pair_diamond_clarity.clarity)
        .join(pair_diamond_cut, pair_diamond.cut == pair_diamond_cut.cut)
        .join(pair_diamond_polish, pair_diamond.polish == pair_diamond_polish.polish)
        .join(pair_diamond_symmetry, pair_diamond.symmetry == pair_diamond_symmetry.symmetry)
        .join(pair_diamond_owner, pair_diamond.id == pair_diamond_owner.diamond_id)
        # Apply the where condition
        .where(
            and_(
                initial_diamond.id.in_(diamonds_ids),
                initial_diamond.shape == pair_diamond.shape,
                pair_diamond.weight.between(initial_diamond.weight * 0.985, initial_diamond.weight * 1.015),
                initial_diamond_color.index.between(pair_diamond_color.index - 1, pair_diamond_color.index + 1),
                initial_diamond_color.group == pair_diamond_color.group,
                initial_diamond_clarity.index.between(pair_diamond_clarity.index - 1, pair_diamond_clarity.index + 1),
                initial_diamond_clarity.group == pair_diamond_clarity.group,
                initial_diamond.length.between(pair_diamond.length * 0.985, pair_diamond.length * 1.015),
                initial_diamond.weight.between(pair_diamond.weight * 0.985, pair_diamond.weight * 1.015),
                initial_diamond.depth_percentage.between(pair_diamond.depth_percentage * 0.985, pair_diamond.depth_percentage * 1.015),
                initial_diamond_cut.index.between(pair_diamond_cut.index - 1, pair_diamond_cut.index + 1),
                initial_diamond_polish.index.between(pair_diamond_polish.index - 1, pair_diamond_polish.index + 1),
                initial_diamond_symmetry.index.between(pair_diamond_symmetry.index - 1, pair_diamond_symmetry.index + 1),
                initial_diamond.fluorescence == pair_diamond.fluorescence,
                pair_diamond.table.between(initial_diamond.table * 0.985, initial_diamond.table * 1.015),
                pair_diamond.depth_percentage.between(initial_diamond.depth_percentage * 0.985, initial_diamond.depth_percentage * 1.015),
                initial_diamond_owner.user_id != pair_diamond_owner.user_id
            )
        )
        .group_by(pair_diamond.id)
    )

    logger.debug("Query: {}", query)

    result = await session.execute(query)
    pairs = result.all()

    diamonds = [diamond for pair in pairs for diamond in pair]

    return diamonds
