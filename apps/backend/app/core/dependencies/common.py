from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.ports.unit_of_work import UnitOfWork
from app.core.dependencies.database import get_db_session
from app.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


def get_unit_of_work(
    session: AsyncSession = Depends(get_db_session),
) -> UnitOfWork:
    """
    Provides the application's Unit of Work.
    """

    return SqlAlchemyUnitOfWork(session)