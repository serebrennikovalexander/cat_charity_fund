from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):

    async def get_by_user(self, session: AsyncSession, user: User):
        donations = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return donations.scalars().all()

    async def get_open_donation(
        self,
        session: AsyncSession,
    ):
        """Функция для получения открытого пожертвования."""
        db_donation = await session.execute(
            select(Donation).where(Donation.fully_invested == 0)
        )
        return db_donation.scalars().first()


donation_crud = CRUDDonation(Donation)
