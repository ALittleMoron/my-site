from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    ExternalResource,
    ExternalResources,
    Sheets,
)


class FactoryHelper:
    @classmethod
    def resource(
        cls,
        resource_id: int,
        name: str = "RESOURCE",
        url: str = "https://example.com",
        context: str = "Context",
    ) -> ExternalResource:
        return ExternalResource(
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
        answer: str = "",
        interview_expected_answer: str = "",
        sheet: str = "",
        grade: str = "",
        section: str = "",
        subsection: str = "",
        resources: list[ExternalResource] | None = None,
    ) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=item_id,
            question=question,
            status=status,
            answer=answer,
            interview_expected_answer=interview_expected_answer,
            sheet=sheet,
            grade=grade,
            section=section,
            subsection=subsection,
            resources=ExternalResources(values=resources or []),
        )

    @classmethod
    def sheets(cls, values: list[str] | None = None) -> Sheets:
        return Sheets(values=values or [])
