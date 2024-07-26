from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Admin(Base):
    __tablename__ = 'admins'

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), primary_key=True, unique=True)

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    @classmethod
    async def check_user(cls, session: AsyncSession, user_id: int) -> bool:
        return bool(await session.get(cls, user_id))
