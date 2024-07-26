from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from ..database.loader import sessionmaker


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        async with sessionmaker() as session:
            data["session"] = session
            return await handler(event, data)
