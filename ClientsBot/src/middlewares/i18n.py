from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import DEFAULT_LOCALE
from ..services.users import get_language_code


class CustomI18nMiddleware(I18nMiddleware):
    DEFAULT_LANGUAGE_CODE = DEFAULT_LOCALE

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        session: AsyncSession = data["session"]

        if not getattr(event, "from_user"):
            return CustomI18nMiddleware.DEFAULT_LANGUAGE_CODE

        user_id = event.from_user.id
        language_code: str | None = await get_language_code(session=session, user_id=user_id)

        return language_code or self.DEFAULT_LANGUAGE_CODE
