from enum import Enum

import aiohttp
from aiohttp import ServerDisconnectedError

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import PAYMENT_PROVIDER_TERMINAL, PAYMENT_PROVIDER_USERNAME, DEFAULT_LOCALE, bot
from ..database.models import GeneratedToken, PaymentPurposePrice
from ..database.models.enums import PaymentPurpose
from .users import get_language_code


class CoinId(Enum):
    Shekel = 1
    USD = 2


async def get_success_redirect_url(purpose: PaymentPurpose) -> str:
    match purpose:
        case PaymentPurpose.SUBSCRIPTION_RENEWAL:
            bot_username = (await bot.get_me()).username
            return f"https://t.me/{bot_username}"
        case PaymentPurpose.CONTACTS_PURCHASE:
            bot_username = (await bot.get_me()).username
            return f"https://t.me/{bot_username}"


async def get_failed_redirect_url(purpose: PaymentPurpose) -> str:
    bot_username = (await bot.get_me()).username
    match purpose:
        case PaymentPurpose.SUBSCRIPTION_RENEWAL:
            return f"https://t.me/{bot_username}"
        case PaymentPurpose.CONTACTS_PURCHASE:
            return f"https://t.me/{bot_username}"


class PaymentLinkGenerationError(Exception):
    pass


async def create_payment_url(session: AsyncSession, author_full_name: str, author_user_id: int,
                             purpose: PaymentPurpose) -> str:
    url = "https://secure.cardcom.solutions/api/v11/LowProfile/Create"
    backend_webhook_url = "https://0532-178-138-35-92.ngrok-free.app/api/v1/payment_request"

    token_instance = await GeneratedToken.generate(session, author_user_id, purpose)
    user_language_code = await get_language_code(session, author_user_id) or DEFAULT_LOCALE
    usd_price = await PaymentPurposePrice.get(session, purpose)

    request_json = {
        "TerminalNumber": PAYMENT_PROVIDER_TERMINAL,
        "ApiName": PAYMENT_PROVIDER_USERNAME,
        "ReturnValue": str(token_instance.value),
        "Amount": usd_price,
        "SuccessRedirectUrl": await get_success_redirect_url(purpose),
        "FailedRedirectUrl": await get_failed_redirect_url(purpose),
        "WebHookUrl": backend_webhook_url,
        "Document": {
            "Name": author_full_name,
            "Email": "",
            "Products": [
                {
                    "Description": purpose.value,
                    "UnitCost": usd_price,
                }
            ]
        },
        "MaxNumOfPayments": 1,
        "ISOCoinId": CoinId.USD.value,
        "Language": user_language_code,
        # "UIDefinition": {
        #     "IsHideCardOwnerPhone": False,
        #     "IsCardOwnerPhoneRequired": True,
        #     "IsHideCardOwnerEmail": False,
        # }
    }

    logger.debug("Request json: {}", request_json)

    async with aiohttp.ClientSession() as client:
        try:
            async with client.post(url, json=request_json) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error("Failed to generate payment url. Status code: {}; response: {}", response.status, text)
                    raise PaymentLinkGenerationError(
                        f"Failed to generate payment url. Status code: {response.status}; response: {text}")

                response_json = await response.json()
                response_url = response_json.get("Url")
                if response_url is None:
                    text = await response.text()
                    logger.error("Failed to generate payment url, because Url key is not found in the response: {}", text)
                    raise PaymentLinkGenerationError(
                        f"Failed to generate payment url, because Url key is not found in the response: {text}")
        except ServerDisconnectedError:
            logger.exception("Failed to generate payment url due to server disconnection")
            raise PaymentLinkGenerationError("Failed to generate payment url due to server disconnection")

    return response_url
