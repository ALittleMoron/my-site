import re
import uuid
from datetime import UTC, datetime
from typing import Any

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser, User
from core.auth.types import Token
from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.schemas import (
    AttachedExternalResource,
    AttachedExternalResources,
    CompetencyMatrixItem,
    CompetencyMatrixItemCreateParams,
    CompetencyMatrixItems,
    CompetencyMatrixItemUpdateParams,
    ExistingExternalResourceAttachment,
    ExternalResource,
    ExternalResources,
    NewExternalResourceAttachment,
    Sheet,
    Sheets,
)
from core.contacts.schemas import ContactMe
from core.enums import PublishStatusEnum
from core.files.schemas import PresignPutObject, PresignPutObjectParams
from core.files.types import Namespace
from core.notes.schemas import Note, NoteMetadata, NoteReactionCounts, Notes, Tag, Tags
from core.schemas import Secret
from core.types import IntId, SearchName


class CoreFactoryHelper:
    @classmethod
    def external_resource(
        cls,
        resource_id: Any,
        name: str = "RESOURCE",
        name_ru: str | None = None,
        name_en: str | None = None,
        url: str = "https://example.com",
    ) -> ExternalResource:
        return ExternalResource(
            id=cls.int_id(resource_id) if isinstance(resource_id, int) else resource_id,
            name_ru=name_ru or name,
            name_en=name_en or name,
            url=url,
        )

    @classmethod
    def external_resources(
        cls,
        values: list[ExternalResource] | None = None,
    ) -> ExternalResources:
        return ExternalResources(values=values or [])

    @classmethod
    def attached_external_resource(
        cls,
        resource_id: Any,
        name: str = "RESOURCE",
        name_ru: str | None = None,
        name_en: str | None = None,
        url: str = "https://example.com",
        context: str = "Context",
        context_ru: str | None = None,
        context_en: str | None = None,
    ) -> AttachedExternalResource:
        return AttachedExternalResource(
            id=cls.int_id(resource_id) if isinstance(resource_id, int) else resource_id,
            name_ru=name_ru or name,
            name_en=name_en or name,
            url=url,
            context_ru=context_ru or context,
            context_en=context_en or context,
        )

    @classmethod
    def attached_external_resources(
        cls,
        values: list[AttachedExternalResource] | None = None,
    ) -> AttachedExternalResources:
        return AttachedExternalResources(values=values or [])

    @classmethod
    def existing_external_resource_attachment(
        cls,
        resource_id: Any,
        context: str = "Context",
        context_ru: str | None = None,
        context_en: str | None = None,
    ) -> ExistingExternalResourceAttachment:
        return ExistingExternalResourceAttachment(
            resource_id=cls.int_id(resource_id) if isinstance(resource_id, int) else resource_id,
            context_ru=context_ru or context,
            context_en=context_en or context,
        )

    @classmethod
    def new_external_resource_attachment(
        cls,
        resource_id: Any,
        name: str = "RESOURCE",
        name_ru: str | None = None,
        name_en: str | None = None,
        url: str = "https://example.com",
        context: str = "Context",
        context_ru: str | None = None,
        context_en: str | None = None,
    ) -> NewExternalResourceAttachment:
        return NewExternalResourceAttachment(
            resource=cls.external_resource(
                resource_id=resource_id,
                name=name,
                name_ru=name_ru,
                name_en=name_en,
                url=url,
            ),
            context_ru=context_ru or context,
            context_en=context_en or context,
        )

    @classmethod
    def competency_matrix_item(
        cls,
        item_id: int,
        slug: str | None = None,
        question: str = "QUESTION",
        question_ru: str | None = None,
        question_en: str | None = None,
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        answer_ru: str | None = None,
        answer_en: str | None = None,
        interview_expected_answer: str = "Answer",
        interview_expected_answer_ru: str | None = None,
        interview_expected_answer_en: str | None = None,
        sheet_key: str | None = None,
        sheet: str = "Sheet",
        sheet_ru: str | None = None,
        sheet_en: str | None = None,
        grade: GradeEnum | None = GradeEnum.JUNIOR,
        section: str = "Section",
        section_ru: str | None = None,
        section_en: str | None = None,
        subsection: str = "Subsection",
        subsection_ru: str | None = None,
        subsection_en: str | None = None,
        resources: list[AttachedExternalResource] | None = None,
    ) -> CompetencyMatrixItem:
        question_en_value = question_en or question
        return CompetencyMatrixItem(
            id=cls.int_id(item_id),
            slug=slug or slugify(question_en_value),
            question_ru=question_ru or question,
            question_en=question_en_value,
            publish_status=publish_status,
            answer_ru=answer_ru or answer,
            answer_en=answer_en or answer,
            interview_expected_answer_ru=interview_expected_answer_ru or interview_expected_answer,
            interview_expected_answer_en=interview_expected_answer_en or interview_expected_answer,
            sheet_key=sheet_key or sheet.lower().replace(" ", "-"),
            sheet_ru=sheet_ru or sheet,
            sheet_en=sheet_en or sheet,
            grade=grade,
            section_ru=section_ru or section,
            section_en=section_en or section,
            subsection_ru=subsection_ru or subsection,
            subsection_en=subsection_en or subsection,
            resources=AttachedExternalResources(values=resources or []),
        )

    @classmethod
    def competency_matrix_item_create_params(
        cls,
        item_id: int,
        slug: str | None = None,
        question: str = "QUESTION",
        question_ru: str | None = None,
        question_en: str | None = None,
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        answer_ru: str | None = None,
        answer_en: str | None = None,
        interview_expected_answer: str = "Answer",
        interview_expected_answer_ru: str | None = None,
        interview_expected_answer_en: str | None = None,
        sheet_key: str | None = None,
        sheet: str = "Sheet",
        sheet_ru: str | None = None,
        sheet_en: str | None = None,
        grade: GradeEnum = GradeEnum.JUNIOR,
        section: str = "Section",
        section_ru: str | None = None,
        section_en: str | None = None,
        subsection: str = "Subsection",
        subsection_ru: str | None = None,
        subsection_en: str | None = None,
        resources: (
            list[ExistingExternalResourceAttachment | NewExternalResourceAttachment] | None
        ) = None,
    ) -> CompetencyMatrixItemCreateParams:
        question_en_value = question_en or question
        return CompetencyMatrixItemCreateParams(
            id=cls.int_id(item_id),
            slug=slug or slugify(question_en_value),
            question_ru=question_ru or question,
            question_en=question_en_value,
            publish_status=publish_status,
            answer_ru=answer_ru or answer,
            answer_en=answer_en or answer,
            interview_expected_answer_ru=interview_expected_answer_ru or interview_expected_answer,
            interview_expected_answer_en=interview_expected_answer_en or interview_expected_answer,
            sheet_key=sheet_key or sheet.lower().replace(" ", "-"),
            sheet_ru=sheet_ru or sheet,
            sheet_en=sheet_en or sheet,
            grade=grade,
            section_ru=section_ru or section,
            section_en=section_en or section,
            subsection_ru=subsection_ru or subsection,
            subsection_en=subsection_en or subsection,
            resources=resources or [],
        )

    @classmethod
    def competency_matrix_item_update_params(
        cls,
        item_id: int,
        slug: str | None = None,
        question: str = "QUESTION",
        question_ru: str | None = None,
        question_en: str | None = None,
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        answer: str = "Answer",
        answer_ru: str | None = None,
        answer_en: str | None = None,
        interview_expected_answer: str = "Answer",
        interview_expected_answer_ru: str | None = None,
        interview_expected_answer_en: str | None = None,
        sheet_key: str | None = None,
        sheet: str = "Sheet",
        sheet_ru: str | None = None,
        sheet_en: str | None = None,
        grade: GradeEnum = GradeEnum.JUNIOR,
        section: str = "Section",
        section_ru: str | None = None,
        section_en: str | None = None,
        subsection: str = "Subsection",
        subsection_ru: str | None = None,
        subsection_en: str | None = None,
        resources: (
            list[ExistingExternalResourceAttachment | NewExternalResourceAttachment] | None
        ) = None,
    ) -> CompetencyMatrixItemUpdateParams:
        question_en_value = question_en or question
        return CompetencyMatrixItemUpdateParams(
            id=cls.int_id(item_id),
            slug=slug or slugify(question_en_value),
            question_ru=question_ru or question,
            question_en=question_en_value,
            publish_status=publish_status,
            answer_ru=answer_ru or answer,
            answer_en=answer_en or answer,
            interview_expected_answer_ru=interview_expected_answer_ru or interview_expected_answer,
            interview_expected_answer_en=interview_expected_answer_en or interview_expected_answer,
            sheet_key=sheet_key or sheet.lower().replace(" ", "-"),
            sheet_ru=sheet_ru or sheet,
            sheet_en=sheet_en or sheet,
            grade=grade,
            section_ru=section_ru or section,
            section_en=section_en or section,
            subsection_ru=subsection_ru or subsection,
            subsection_en=subsection_en or subsection,
            resources=resources or [],
        )

    @classmethod
    def sheet(
        cls,
        key: str = "python",
        name: str = "Python",
        name_ru: str | None = None,
        name_en: str | None = None,
    ) -> Sheet:
        return Sheet(key=key, name_ru=name_ru or name, name_en=name_en or name)

    @classmethod
    def sheets(cls, values: list[Sheet] | list[str] | None = None) -> Sheets:
        if values is None:
            return Sheets(values=[])
        return Sheets(
            values=[
                cls.sheet(key=value.lower(), name=value) if isinstance(value, str) else value
                for value in values
            ],
        )

    @classmethod
    def user(
        cls,
        username: str = "",
        password_hash: str = "",
        role: RoleEnum = RoleEnum.USER,
    ) -> User:
        return User(username=username, password_hash=Secret(password_hash), role=role)

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
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> ContactMe:
        return ContactMe(
            id=contact_me_id or uuid.uuid4(),
            name=name,
            email=email,
            telegram=telegram,
            message=message,
        )

    @classmethod
    def note(
        cls,
        note_id: uuid.UUID | None = None,
        title: str = "Test Note",
        content: str = "This is a test note content.",
        slug: str = "test-notes-note",
        folder: str = "General",
        title_ru: str | None = None,
        title_en: str | None = None,
        content_ru: str | None = None,
        content_en: str | None = None,
        folder_ru: str | None = None,
        folder_en: str | None = None,
        seo_title_ru: str | None = None,
        seo_title_en: str | None = None,
        seo_description_ru: str | None = None,
        seo_description_en: str | None = None,
        cover_image_url: str | None = None,
        cover_image_alt_ru: str | None = None,
        cover_image_alt_en: str | None = None,
        metadata: NoteMetadata | None = None,
        author_username: str = "admin",
        publish_status: PublishStatusEnum = PublishStatusEnum.PUBLISHED,
        published_at: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        tags: list[Tag] | None = None,
    ) -> Note:
        now = datetime.now(tz=UTC)
        return Note(
            id=note_id or uuid.uuid4(),
            slug=slug,
            title_ru=title_ru or title,
            title_en=title_en or title,
            content_ru=content_ru or content,
            content_en=content_en or content,
            folder_ru=folder_ru or folder,
            folder_en=folder_en or folder,
            author_username=author_username,
            metadata=metadata
            or NoteMetadata(
                seo_title_ru=seo_title_ru,
                seo_title_en=seo_title_en,
                seo_description_ru=seo_description_ru,
                seo_description_en=seo_description_en,
                cover_image_url=cover_image_url,
                cover_image_alt_ru=cover_image_alt_ru,
                cover_image_alt_en=cover_image_alt_en,
            ),
            publish_status=publish_status,
            published_at=(
                datetime.fromisoformat(published_at).replace(tzinfo=UTC)
                if published_at is not None
                else None
            ),
            created_at=(
                datetime.fromisoformat(created_at).replace(tzinfo=UTC)
                if created_at is not None
                else now
            ),
            updated_at=(
                datetime.fromisoformat(updated_at).replace(tzinfo=UTC)
                if updated_at is not None
                else now
            ),
            tags=Tags(values=tags or []),
        )

    @classmethod
    def note_list(
        cls,
        notes: list[Note] | None = None,
        total_count: int = 0,
        total_pages: int = 0,
    ) -> Notes:
        return Notes(values=notes or [], total_count=total_count, total_pages=total_pages)

    @classmethod
    def tag(
        cls,
        tag_id: IntId | int = 1,
        name: str = "Python",
        name_ru: str | None = None,
        name_en: str | None = None,
        slug: str = "python",
        deleted_at: str | None = None,
    ) -> Tag:
        return Tag(
            id=cls.int_id(tag_id) if isinstance(tag_id, int) else tag_id,
            name_ru=name_ru or name,
            name_en=name_en or name,
            slug=slug,
            deleted_at=(
                datetime.fromisoformat(deleted_at).replace(tzinfo=UTC)
                if deleted_at is not None
                else None
            ),
        )

    @classmethod
    def tags(cls, values: list[Tag] | None = None) -> Tags:
        return Tags(values=values or [])

    @classmethod
    def note_reaction_counts(
        cls,
        heart: int = 0,
        fire: int = 0,
        thinking: int = 0,
        neutral: int = 0,
        poop: int = 0,
    ) -> NoteReactionCounts:
        return NoteReactionCounts(
            heart=heart,
            fire=fire,
            thinking=thinking,
            neutral=neutral,
            poop=poop,
        )

    @classmethod
    def jwt_user(
        cls,
        username: str = "test",
        role: RoleEnum = RoleEnum.ADMIN,
    ) -> JwtUser:
        return JwtUser(username=username, role=role)

    @classmethod
    def presign_put_object_params(
        cls,
        folder: str = "folder",
        namespace: Namespace = "media",
        content_type: str = "application/octet-stream",
    ) -> PresignPutObjectParams:
        return PresignPutObjectParams(
            folder=folder,
            namespace=namespace,
            content_type=content_type,
        )

    @classmethod
    def presign_put_object(
        cls,
        upload_url: str = "http://localhost/upload_url",
        access_url: str = "http://localhost/access_url",
    ) -> PresignPutObject:
        return PresignPutObject(upload_url=upload_url, access_url=access_url)

    @classmethod
    def token(cls, value: bytes) -> Token:
        return Token(value)

    @classmethod
    def int_id(cls, value: int) -> IntId:
        return IntId(value)

    @classmethod
    def search_name(cls, value: Any) -> SearchName:
        return SearchName(value)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
