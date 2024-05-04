from typing import Union

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import TelegramUser


class TelegramUserDAL:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_user(self, telegram_id: int) -> TelegramUser:
        stmt = select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
        user = await self.session.execute(stmt)
        return user.scalars().first()

    async def create_user(
            self,
            telegram_id: int,
            first_name: str,
            last_name: str,
            language: str,
            username: Union[str, None] = None
    ) -> bool:
        stmt = insert(TelegramUser).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            language=language,
            username=username,
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return True

    async def update_language(self, user_id: int, language: str) -> bool:
        stmt = update(TelegramUser).where(TelegramUser.id == user_id).values(language=language)
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return True