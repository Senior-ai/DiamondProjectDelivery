from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import SuccessfulTokenPayment, ActivatedSubscription, GeneratedToken, SubscriptionType, \
    PaymentPurposePrice
from ..database.models.enums import PaymentPurpose


class TokenPaymentError(Exception):
    pass


class TokenNotFoundError(TokenPaymentError):
    pass


class UnknownTokenPurpose(TokenPaymentError):
    pass


async def make_token_payment(session: AsyncSession, payment_request_id: int, token_value: str):
    logger.info("Making token payment with token {}", token_value)
    token_information = await GeneratedToken.get(session, token_value)

    if token_information is None:
        logger.error("Token {} not found", token_value)
        raise TokenNotFoundError("Token not found")

    match token_information:
        case GeneratedToken(purpose=PaymentPurpose.SUBSCRIPTION_RENEWAL as purpose, author_user_id=author_user_id):
            logger.info("Token {} recognized as subscription renewal", token_value)
            logger.info("Renewing 'Monthly' subscription for user {}", author_user_id)
            subscription_type = await SubscriptionType.get_by_name(session, "Monthly")
            await ActivatedSubscription.create(session, author_user_id, subscription_type.id)
            logger.success("Subscription renewed")
        case GeneratedToken(purpose=PaymentPurpose.CONTACTS_PURCHASE as purpose):
            logger.info("Token {} recognized as contacts purchase", token_value)
        case _:
            # TODO: fix possible unsaved payment
            logger.error("Unknown token {} purpose", token_value)
            raise UnknownTokenPurpose("Unknown token purpose")

    usd_amount = await PaymentPurposePrice.get(session, purpose)

    logger.info("Saving successful token payment for token {}", token_value)
    await SuccessfulTokenPayment.create(session, payment_request_id, token_value, usd_amount)
    logger.success("Token payment was saved")
