import datetime

from app.core.competency_matrix.enums import StatusEnum
from app.core.competency_matrix.schemas import (
    FilledCompetencyMatrixItems,
    FullCompetencyMatrixItem,
    Grade,
    Resource,
    Resources,
    Section,
    Sheet,
    ShortFilledCompetencyMatrixItem,
    Subsection,
)


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
    def sheet(cls, sheet_id: int, name: str = "SHEET") -> Sheet:
        return Sheet(id=sheet_id, name=name)

    @classmethod
    def grade(cls, grade_id: int, name: str = "GRADE") -> Grade:
        return Grade(id=grade_id, name=name)

    @classmethod
    def section(
        cls,
        section_id: int,
        name: str = "SECTION",
        sheet_id: int | None = None,
        sheet: Sheet | None = None,
    ) -> Section:
        return Section(id=section_id, name=name, sheet=sheet or cls.sheet(sheet_id=sheet_id or 1))

    @classmethod
    def subsection(
        cls,
        subsection_id: int,
        name: str = "SUBSECTION",
        section_id: int | None = None,
        section: Section | None = None,
    ) -> Subsection:
        return Subsection(
            id=subsection_id,
            name=name,
            section=section or cls.section(section_id=section_id or 1),
        )

    @classmethod
    def short_filled_competency_matrix_item(
        cls,
        item_id: int,
        question: str,
        status: StatusEnum = StatusEnum.PUBLISHED,
        status_changed: datetime.datetime | None = None,
        grade_id: int = 1,
        subsection_id: int = 1,
    ) -> ShortFilledCompetencyMatrixItem:
        return ShortFilledCompetencyMatrixItem(
            id=item_id,
            question=question,
            status=status,
            status_changed=status_changed or datetime.datetime.now(tz=datetime.UTC),
            grade_id=grade_id,
            subsection_id=subsection_id,
        )

    @classmethod
    def filled_competency_matrix_items(
        cls,
        values: list[ShortFilledCompetencyMatrixItem] | None = None,
    ) -> FilledCompetencyMatrixItems:
        return FilledCompetencyMatrixItems(values=values or [])

    @classmethod
    def full_competency_matrix_item(
        cls,
        item_id: int,
        question: str = "TEST",
        status: StatusEnum = StatusEnum.PUBLISHED,
        status_changed: datetime.datetime | None = None,
        answer: str = "ANSWER",
        interview_expected_answer: str = "INTERVIEW",
        grade_id: int | None = None,
        grade: Grade | None = None,
        subsection_id: int | None = None,
        subsection: Subsection | None = None,
        resources: list[Resource] | None = None,
    ) -> FullCompetencyMatrixItem:
        if (grade and not grade_id) or (subsection and not subsection_id):
            msg = "grade or subsection required, if their ids are passed."
            raise ValueError(msg)
        return FullCompetencyMatrixItem(
            id=item_id,
            question=question,
            status=status,
            status_changed=status_changed or datetime.datetime.now(tz=datetime.UTC),
            grade_id=grade_id,
            subsection_id=subsection_id,
            answer=answer,
            interview_expected_answer=interview_expected_answer,
            grade=grade,
            subsection=subsection,
            resources=Resources(values=resources or []),
        )
