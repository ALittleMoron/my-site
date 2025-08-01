import uuid

from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.schemas import (
    CompetencyMatrixItem,
    ExternalResource,
    ExternalResources,
    Sheets,
    CompetencyMatrixItems,
)
from core.contacts.schemas import ContactMe
from core.schemas import Secret
from core.users.schemas import User, RoleEnum


class CoreFactoryHelper:
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

    @classmethod
    def user(
        cls,
        username: str = "",
        password: str = "",
        role: RoleEnum = RoleEnum.USER,
    ) -> User:
        return User(
            username=username,
            password=Secret(password),
            role=role,
        )

    @classmethod
    def competency_matrix_items(
        cls,
        values: list[CompetencyMatrixItem] | None = None,
    ) -> CompetencyMatrixItems:
        return CompetencyMatrixItems(values=values or [])

    @classmethod
    def contact_me(
        cls,
        contact_me_id: uuid.UUID | None = None,
        user_ip: str = "127.0.0.1",
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> ContactMe:
        return ContactMe(
            id=contact_me_id or uuid.uuid4(),
            user_ip=user_ip,
            name=name,
            email=email,
            telegram=telegram,
            message=message,
        )
