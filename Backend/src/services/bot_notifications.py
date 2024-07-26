import aiohttp
from aiohttp.client_exceptions import ServerDisconnectedError

from ..core.config import SELLERS_BOT_HOST, SELLERS_BOT_PORT, CLIENTS_BOT_HOST, CLIENTS_BOT_PORT
from loguru import logger


class NotifyError(Exception):
    pass


class NotifySellerAboutSuccessfulSubscriptionRenewalError(NotifyError):
    pass


async def notify_seller_about_successful_subscription_renewal(seller_id: int):
    endpoint = f"http://{SELLERS_BOT_HOST}:{SELLERS_BOT_PORT}/api/v1/notify/{{seller}}/successful_subscription_renewal"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint.format(seller=seller_id)) as response:
                status = response.status
        except ServerDisconnectedError:
            logger.exception("Failed to notify seller {}. Server disconnected.", seller_id)
            raise NotifySellerAboutSuccessfulSubscriptionRenewalError(
                f"Failed to notify seller {seller_id}. Server disconnected.")

    if status != 200:
        raise NotifySellerAboutSuccessfulSubscriptionRenewalError(f"Failed to notify seller {seller_id}")


async def notify_client_about_successful_b2b_group_access_purchase(user_id: int):
    endpoint = f"http://{CLIENTS_BOT_HOST}:{CLIENTS_BOT_PORT}/api/v1/notify/{{user}}/successful_b2b_group_access_purchase"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint.format(user=user_id)) as response:
                status = response.status
        except ServerDisconnectedError:
            logger.exception("Failed to notify client {}. Server disconnected.", user_id)
            raise NotifyError(f"Failed to notify client {user_id}. Server disconnected.")

    if status != 200:
        raise NotifyError(f"Failed to notify client {user_id}")


async def notify_seller_about_successful_contacts_purchase(token_value: str):
    endpoint = f"http://{SELLERS_BOT_HOST}:{SELLERS_BOT_PORT}/api/v1/notify/contact_purchase/{{token_value}}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint.format(token_value=token_value)) as response:
                status = response.status
        except ServerDisconnectedError:
            logger.exception("Failed to notify seller {}. Server disconnected.", token_value)
            raise NotifyError(f"Failed to notify seller {token_value}. Server disconnected.")

    if status != 200:
        raise NotifyError(f"Failed to notify seller {token_value}")
