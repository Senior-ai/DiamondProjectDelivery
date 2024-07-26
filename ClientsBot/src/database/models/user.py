from typing import Union

from loguru import logger
from sqlalchemy import String, select, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class UserNotFound(Exception):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    language_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(255), nullable=True)

    @staticmethod
    async def create_user(session: AsyncSession, user_id: int, language_code: str, first_name: str | None = None,
                          last_name: str | None = None, phone_number: str | None = None) -> "User":
        user = User(user_id, language_code, first_name, last_name, phone_number)
        session.add(user)
        await session.commit()
        return user

    @classmethod
    async def update_user(cls, session: AsyncSession, user_id: int, first_name: str | None = None, last_name: str | None = None,
                          phone_number: str | None = None):
        user = await session.get(cls, user_id)
        if user is None:
            raise UserNotFound(f"User with id {user_id} not found")
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        await session.commit()

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    async def set_language_code(self, session: AsyncSession, language_code: str):
        self.language_code = language_code
        await session.commit()

    @classmethod
    async def has_shared_contacts(cls, session: AsyncSession, user_id) -> bool:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user_tuple = result.first()
        logger.debug("Result tuple: {}", result)

        if user_tuple is None:
            return False

        user = user_tuple[0]

        logger.debug("User: {}", user)

        if not user:
            return False
        if not user.phone_number:
            return False
        if not user.first_name:
            return False
        return True

    @classmethod
    async def get(cls, session: AsyncSession, user_id: int) -> Union["User", None]:
        return await session.get(cls, user_id)
