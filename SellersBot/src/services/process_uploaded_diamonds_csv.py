import csv
import io
from datetime import datetime
from typing import List, Dict, Any

from loguru import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.loader import sessionmaker
from .users import get_gettext
from ..csv_validation import CSVValidator, NotEmptyTextValidator, LiteralValidator, NumericValidator, IntegerValidator, \
    MeasurementsValidator, NullableValidator, URLValidator
from ..database.models.enums import shape_aliases, color_aliases, clarity_aliases, quality_aliases, \
    fluorescence_aliases, culet_aliases
from .find_pairs import find_pairs_for_diamonds
from ..database.models import Diamond, DiamondOwner, DiamondAddError, SubscriptionType, ActivatedSubscription


class TotalDiamondsLimitExceededError(Exception):
    pass

class DiamondsPerLoadLimitExceededError(Exception):
    pass


class NoActiveSubscriptionFoundError(Exception):
    pass


csv_file_validator = CSVValidator()
csv_file_validator.add_column('Stock#', [NotEmptyTextValidator()])
csv_file_validator.add_column('Shape', [LiteralValidator(shape_aliases.keys())])
csv_file_validator.add_column('Weight', [NumericValidator()])
csv_file_validator.add_column('Color', [LiteralValidator(color_aliases.keys())])
csv_file_validator.add_column('Clarity', [LiteralValidator(clarity_aliases.keys())])
csv_file_validator.add_column('Lab', [NotEmptyTextValidator()])
csv_file_validator.add_column('CertNumber', [IntegerValidator()])
csv_file_validator.add_column('Measurements', [MeasurementsValidator()])
csv_file_validator.add_column('Ratio', [NumericValidator()])
csv_file_validator.add_column('Cut', [LiteralValidator(quality_aliases.keys())])
csv_file_validator.add_column('Polish', [LiteralValidator(quality_aliases.keys())])
csv_file_validator.add_column('Symm', [LiteralValidator(quality_aliases.keys())])
csv_file_validator.add_column('Fluo', [LiteralValidator(fluorescence_aliases.keys())])
csv_file_validator.add_column('Table', [NumericValidator()])
csv_file_validator.add_column('Depth', [NumericValidator()])
csv_file_validator.add_column('Girdle', [NotEmptyTextValidator()])
csv_file_validator.add_column('Culet', [LiteralValidator(culet_aliases.keys())])
csv_file_validator.add_column('CertComments', [])
csv_file_validator.add_column('Rap%', [NullableValidator(NumericValidator())])
csv_file_validator.add_column('Price/Crt', [NullableValidator(NumericValidator())])
csv_file_validator.add_column('Pic', [NullableValidator(URLValidator())])


class InvalidCSVFileError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__()


async def process_uploaded_diamonds_csv(session: AsyncSession, csv_file: io.TextIOWrapper, user_id: int) -> List[Diamond]:
    _ = await get_gettext(session, user_id)

    diamonds_list: List[Dict[str, Any]] = []
    upload_datetime = datetime.now()

    stmt = (
        select(func.max(SubscriptionType.max_diamonds_per_load), func.max(SubscriptionType.total_new_diamonds_per_period))
        .select_from(ActivatedSubscription)
        .join(SubscriptionType, onclause=ActivatedSubscription.subscription_type_id == SubscriptionType.id)
        .where(
            and_(
                ActivatedSubscription.activation_date + SubscriptionType.duration >= upload_datetime,
                ActivatedSubscription.user_id == user_id
            )
        )
        .group_by(ActivatedSubscription.activation_date)
    )

    result = (await session.execute(stmt)).all()

    if not result:
        raise NoActiveSubscriptionFoundError("No active subscription found.")

    max_diamonds_per_load, max_total_diamonds_amount = result[0]

    csv_file.seek(0)
    try:
        rows_amount = sum(1 for _ in csv_file)
    except UnicodeDecodeError:
        raise InvalidCSVFileError([_("File is not a CSV file.")])
    logger.debug("CSV file rows amount: {}", rows_amount)

    if rows_amount > max_diamonds_per_load:
        raise DiamondsPerLoadLimitExceededError

    if max_total_diamonds_amount < await DiamondOwner.count_for_user(session, user_id) + rows_amount:
        raise TotalDiamondsLimitExceededError("Total diamonds limit exceeded.")

    logger.info("Validating the CSV file.")
    csv_file.seek(0)
    errors = csv_file_validator.validate(csv_file, _, True)
    logger.debug("Validation finished. Errors: {}", errors)

    if errors:
        raise InvalidCSVFileError(errors)
    logger.success("CSV file is valid.")

    logger.info("Starting to process the CSV file.")
    csv_file.seek(0)
    reader = csv.DictReader(csv_file, delimiter=",")

    for row_number, row in enumerate(reader, start=1):
        shape_value = shape_aliases.get(row['Shape'])
        color_value = color_aliases.get(row['Color'])
        clarity_value = clarity_aliases.get(row['Clarity'])
        cut_value = quality_aliases.get(row['Cut'])
        polish_value = quality_aliases.get(row['Polish'])
        symmetry_value = quality_aliases.get(row['Symm'])
        fluorescence_value = fluorescence_aliases.get(row['Fluo'])
        culet_value = culet_aliases.get(row['Culet'])
        length, other = row['Measurements'].split('-')
        width, depth = other.split('x')
        length, width, depth = float(length), float(width), float(depth)

        diamond = {
            'stock': row['Stock#'],
            'shape': shape_value,
            'weight': float(row['Weight']),
            'color': color_value,
            'clarity': clarity_value,
            'lab': row['Lab'],
            'certificate_number': int(row['CertNumber']),
            'length': length,
            'width': width,
            'depth': depth,
            'ratio': float(row['Ratio']),
            'cut': cut_value,
            'polish': polish_value,
            'symmetry': symmetry_value,
            'fluorescence': fluorescence_value,
            'table': float(row['Table']),
            'depth_percentage': float(row['Depth']),
            'gridle': row['Girdle'],
            'culet': culet_value,
            'certificate_comment': row['CertComments'] or None,
            'rapnet': float(row['Rap%']) if row['Rap%'] else None,
            'price_per_carat': float(row['Price/Crt']) if row['Price/Crt'] else None,
            'picture': row['Pic'] if row['Pic'] else None,
        }

        logger.debug("Diamond created: {}", diamond)

        diamonds_list.append(diamond)

    logger.success("File was processed and validated.")

    logger.info("Adding diamonds to the database.")
    try:
        diamond_ids = await Diamond.add_diamonds(session, diamonds_list)
    except DiamondAddError as e:
        logger.exception("An error occurred while adding diamonds to the database: {}", e)
        raise
    logger.info("Adding diamond owners to the database.")
    await DiamondOwner.make_user(session, user_id, diamond_ids, upload_datetime)
    logger.success("Diamonds were added to the database.")

    return await find_pairs_for_diamonds(session, diamond_ids)
