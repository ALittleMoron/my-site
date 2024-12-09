from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.competency_matrix.deps import dependencies as competency_matrix_dependencies
from app.database.storages import CompetencyMatrixStorage, DatabaseStorage


async def build_storage(db_session: AsyncSession) -> CompetencyMatrixStorage:
    return DatabaseStorage(session=db_session)


dependencies = {'storage': Provide(build_storage), **competency_matrix_dependencies}
