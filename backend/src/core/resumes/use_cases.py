from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime

from core.resumes.schemas import (
    Resume,
    ResumeCreateParams,
    ResumeFilters,
    Resumes,
    ResumeUpdateParams,
)
from core.resumes.storages import ResumesStorage
from core.types import IntId


class AbstractResumesUseCase(ABC):
    @abstractmethod
    async def list_resumes(self, *, filters: ResumeFilters) -> Resumes:
        raise NotImplementedError

    @abstractmethod
    async def get_resume(self, *, resume_id: IntId, author_username: str) -> Resume:
        raise NotImplementedError

    @abstractmethod
    async def create_resume(self, *, params: ResumeCreateParams) -> Resume:
        raise NotImplementedError

    @abstractmethod
    async def update_resume(
        self,
        *,
        resume_id: IntId,
        params: ResumeUpdateParams,
        author_username: str,
    ) -> Resume:
        raise NotImplementedError

    @abstractmethod
    async def delete_resume(self, *, resume_id: IntId, author_username: str) -> None:
        raise NotImplementedError


@dataclass(kw_only=True, slots=True, frozen=True)
class ResumesUseCase(AbstractResumesUseCase):
    storage: ResumesStorage

    async def list_resumes(self, *, filters: ResumeFilters) -> Resumes:
        if filters.page is None or filters.page_size is None:
            message = "pagination required"
            raise ValueError(message)
        resumes, total_count = await self.storage.list_resumes(filters=filters)
        return Resumes.from_page(
            values=resumes,
            total_count=total_count,
            page_size=filters.page_size,
        )

    async def get_resume(self, *, resume_id: IntId, author_username: str) -> Resume:
        return await self.storage.get_resume(
            resume_id=resume_id,
            author_username=author_username,
        )

    async def create_resume(self, *, params: ResumeCreateParams) -> Resume:
        return await self.storage.create_resume(params=params)

    async def update_resume(
        self,
        *,
        resume_id: IntId,
        params: ResumeUpdateParams,
        author_username: str,
    ) -> Resume:
        existing_resume = await self.storage.get_resume(
            resume_id=resume_id,
            author_username=author_username,
        )
        now = datetime.now(tz=UTC)
        return await self.storage.update_resume(
            resume=params.to_resume(existing_resume=existing_resume, now=now),
        )

    async def delete_resume(self, *, resume_id: IntId, author_username: str) -> None:
        await self.storage.delete_resume(resume_id=resume_id, author_username=author_username)
