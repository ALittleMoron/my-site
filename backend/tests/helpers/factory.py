from datetime import UTC, datetime

from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.schemas import CompetencyMatrixItem, Resource, Resources, Sheets


class FactoryHelper:
    @classmethod
    def resource(
        cls,
        resource_id: int,
        name: str = "RESOURCE",
        url: str = "https://example.com",
        context: str = "Context",
    ) -> Resource:
        return Resource(
            id=resource_id,
            name=name,
            url=url,
            context=context,
        )

    @classmethod
    def competency_matrix_item(
        cls,
        item_id: int,
        question: str,
        status: StatusEnum = StatusEnum.PUBLISHED,
        status_changed: datetime | None = None,
        answer: str = "",
        interview_expected_answer: str = "",
        sheet: str = "",
        grade: str = "",
        section: str = "",
        subsection: str = "",
        resources: list[Resource] | None = None,
    ) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=item_id,
            question=question,
            status=status,
            status_changed=status_changed or datetime.now(tz=UTC),
            answer=answer,
            interview_expected_answer=interview_expected_answer,
            sheet=sheet,
            grade=grade,
            section=section,
            subsection=subsection,
            resources=Resources(values=resources or []),
        )

    @classmethod
    def sheets(cls, values: list[str] | None = None) -> Sheets:
        return Sheets(values=values or [])
