from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from ..services.users import user_exists, add_user


class RegistrationMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:

        if not getattr(event, "from_user"):
            await handler(event, data)

        user_id = event.from_user.id
        session = data["session"]

        if not await user_exists(session=session, user_id=user_id):
            await add_user(session=session, user=event.from_user)

        await handler(event, data)
