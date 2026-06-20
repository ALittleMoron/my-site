from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.resumes.storages import ResumesStorage
from core.resumes.use_cases import ResumesUseCase
from infra.postgresql.storages.resumes import ResumesDatabaseStorage


class ResumesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_resumes_storage(self, session: AsyncSession) -> ResumesStorage:
        return ResumesDatabaseStorage(session=session)

    @provide(scope=Scope.REQUEST)
    async def provide_resumes_use_case(self, storage: ResumesStorage) -> ResumesUseCase:
        return ResumesUseCase(storage=storage)
