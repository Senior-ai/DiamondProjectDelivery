from json import JSONDecodeError

from fastapi import Request, Response
from loguru import logger

from ...database.models import GeneratedToken, ReceivedPaymentRequests
from ...database.models.enums import PaymentPurpose
from ...services import notify_seller_about_successful_subscription_renewal, \
    NotifySellerAboutSuccessfulSubscriptionRenewalError, NotifyError, \
    notify_client_about_successful_b2b_group_access_purchase, notify_seller_about_successful_contacts_purchase
from ...services import make_token_payment, TokenNotFoundError, UnknownTokenPurpose, TokenPaymentError
from ...database.loader import sessionmaker
from ..router import router


@router.post('/payment_request', status_code=200, include_in_schema=False)
async def payment_request(request: Request):
    logger.success("Token payment request received")

    try:
        request_json = await request.json()
    except JSONDecodeError:
        logger.exception("Invalid json received")
        return Response(status_code=400, content="Invalid json")

    logger.info("Creating database session")
    async with sessionmaker() as session:
        logger.info("Saving payment request...")
        saved_payment_request = await ReceivedPaymentRequests.add(session, request_json)
        logger.success("Payment request saved with id: {}", saved_payment_request.id)

    token_value = request_json.get("ReturnValue")
    if token_value is None:
        logger.warning("Invalid request received. No ReturnValue key found. Request json: {}", request_json)
        return Response(status_code=400, content="No ReturnValue key in the request")

    logger.info("Creating database session")
    async with sessionmaker() as session:
        try:
            await make_token_payment(session, saved_payment_request.id, token_value)
        except TokenNotFoundError:
            logger.exception("Unknown token received: {}", token_value)
            return Response(status_code=400, content="Unknown token provided as a ReturnValue key")
        except UnknownTokenPurpose:
            logger.exception("Unknown token purpose. This must never happen!")
            return Response(status_code=500, content="Unknown token purpose")
        except TokenPaymentError:
            logger.exception("Token payment error. This must never happen!")
            return Response(status_code=500, content="Token payment error")

        token = await GeneratedToken.get(session, token_value)

    match token:
        case GeneratedToken(purpose=PaymentPurpose.SUBSCRIPTION_RENEWAL, author_user_id=seller_id):
            try:
                await notify_seller_about_successful_subscription_renewal(seller_id)
            except (NotifySellerAboutSuccessfulSubscriptionRenewalError, NotifyError):
                logger.exception("Error while notifying seller {} about successful subscription renewal",
                                 seller_id)
                return Response(status_code=500, content="Error while notifying seller")
            else:
                logger.success("Seller {} was notified about successful subscription renewal", seller_id)
        case GeneratedToken(purpose=PaymentPurpose.CONTACTS_PURCHASE, author_user_id=seller_id):
            try:
                await notify_seller_about_successful_contacts_purchase(token_value)
            except NotifyError:
                logger.exception("Error while notifying seller {} about successful contacts purchase",
                                 seller_id)
                return Response(status_code=500, content="Error while notifying seller")
            else:
                logger.success("Seller {} was notified about successful contacts purchase")
        case GeneratedToken(purpose=PaymentPurpose.B2B_GROUP_ACCESS, author_user_id=user_id):
            try:
                await notify_client_about_successful_b2b_group_access_purchase(user_id)
            except NotifyError:
                logger.exception("Error while notifying client {} about successful b2b group access purchase",
                                 user_id)
                return Response(status_code=500, content="Error while notifying client")
            else:
                logger.success("Client {} was notified about successful b2b group access purchase", user_id)
        case _:
            logger.error("Unknown token purpose. This must never happen!")

    logger.success("Payment request processed")
