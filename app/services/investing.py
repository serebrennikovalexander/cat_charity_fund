from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation, User
from app.schemas.charity_project import CharityProjectCreate
from app.schemas.donation import DonationCreate


async def get_open_charity_project(
    session: AsyncSession,
):
    """Функция для получения открытого проекта."""

    db_charity_project = await session.execute(
        select(CharityProject).where(CharityProject.fully_invested == False)
    )

    return db_charity_project.scalars().first()


async def get_open_donation(
    session: AsyncSession,
):
    """Функция для получения открытого пожертвования."""

    db_donation = await session.execute(
        select(Donation).where(Donation.fully_invested == False)
    )

    return db_donation.scalars().first()


async def create_charity_project_investing(
    charity_project: CharityProjectCreate,
    session: AsyncSession,
) -> CharityProject:
    """Функция инвестирования при создании проекта."""

    new_project_data = charity_project.dict()

    new_project_data["invested_amount"] = 0

    while (
        new_project_data["full_amount"] > new_project_data["invested_amount"]
    ):
        # Ищем открытое пожертвование
        donation = await get_open_donation(session)

        # Если открытое пожертвование существет то выполняем следующие действия
        if donation is not None:
            donation_amount_delta = (
                donation.full_amount - donation.invested_amount
            )

            project_amount_delta = (
                new_project_data["full_amount"] -
                new_project_data["invested_amount"]
            )
            # Рассматриваем три случая

            # Первый случай
            if donation_amount_delta > project_amount_delta:
                donation.invested_amount += project_amount_delta
                new_project_data["invested_amount"] = (
                    charity_project.full_amount
                )
                new_project_data["fully_invested"] = True
                new_project_data["close_date"] = datetime.utcnow()
                break

            # Второй случай
            if donation_amount_delta == project_amount_delta:
                donation.invested_amount = donation.full_amount
                donation.fully_invested = True
                new_project_data["invested_amount"] = (
                    charity_project.full_amount
                )
                new_project_data["fully_invested"] = True
                new_project_data["close_date"] = datetime.utcnow()
                donation.close_date = datetime.utcnow()
                break

            # Третий случай
            if donation_amount_delta < project_amount_delta:
                donation.invested_amount = donation.full_amount
                donation.fully_invested = True
                donation.close_date = datetime.utcnow()
                new_project_data["invested_amount"] += donation_amount_delta
        else:
            break

    db_project = CharityProject(**new_project_data)

    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project


async def create_donation_investing(
    new_donation: DonationCreate,
    session: AsyncSession,
    user: Optional[User] = None,
) -> Donation:
    """Функция инвестирования при создании пожертвования."""

    new_donation_data = new_donation.dict()

    if user is not None:
        new_donation_data["user_id"] = user.id

    new_donation_data["invested_amount"] = 0

    while (
        new_donation_data["full_amount"] > new_donation_data["invested_amount"]
    ):
        # Ищем открытый проекты
        charity_project = await get_open_charity_project(session)

        # Если открытый проек существет то выполняем следующие действия
        if charity_project is not None:
            project_amount_delta = (
                charity_project.full_amount - charity_project.invested_amount
            )

            donation_amount_delta = (
                new_donation_data["full_amount"] -
                new_donation_data["invested_amount"]
            )

            # Рассматриваем три случая

            # Первый случай
            if project_amount_delta > donation_amount_delta:
                charity_project.invested_amount += donation_amount_delta
                new_donation_data["invested_amount"] = new_donation.full_amount
                new_donation_data["fully_invested"] = True
                new_donation_data["close_date"] = datetime.utcnow()
                break

            # Второй случай
            if project_amount_delta == donation_amount_delta:
                charity_project.invested_amount = charity_project.full_amount
                charity_project.fully_invested = True
                new_donation_data["invested_amount"] = new_donation.full_amount
                new_donation_data["fully_invested"] = True
                charity_project.close_date = datetime.utcnow()
                break

            # Третий случай
            if project_amount_delta < donation_amount_delta:
                charity_project.invested_amount = charity_project.full_amount
                charity_project.fully_invested = True
                charity_project.close_date = datetime.utcnow()
                new_donation_data["invested_amount"] += project_amount_delta

        else:
            break

    db_donation = Donation(**new_donation_data)

    session.add(db_donation)
    await session.commit()
    await session.refresh(db_donation)
    return db_donation
