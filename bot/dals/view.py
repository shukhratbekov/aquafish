from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.view import Review


class ReviewDAL:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_view(self, user_id, view):
        stmt = insert(Review).values(telegram_user_id=user_id, view=view).returning(Review.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return result.fetchone()[0]

    async def get_view(self, review_id):
        stmt = select(Review).where(Review.id == review_id)
        view = await self.session.scalar(stmt)
        await self.session.close()
        return view
