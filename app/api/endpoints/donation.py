from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import (DonationCreate, DonationFullDB,
                                  DonationSmallDB)
from app.services.investing import create_donation_investing

router = APIRouter()


@router.post(
    "/",
    response_model=DonationSmallDB,
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Только для зарегистрированных пользовтаелей."""
    new_donation = await create_donation_investing(donation, session, user)

    return new_donation


@router.get(
    "/",
    response_model=list[DonationFullDB],
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    all_donations = await donation_crud.get_multi(session=session)
    return all_donations


@router.get(
    "/my",
    response_model=list[DonationSmallDB],
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Получает список всех пожертвований для текущего пользователя."""
    donations = await donation_crud.get_by_user(session=session, user=user)
    return donations
