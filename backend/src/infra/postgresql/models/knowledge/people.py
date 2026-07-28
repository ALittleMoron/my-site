from typing import Self

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_dev_utils.mixins.audit import AuditMixin

from core.knowledge.people.schemas import (
    PersonBirthday,
    PersonDetails,
    PersonRelationship,
    PersonRelationshipType,
    PersonRelationshipTypeCreateParams,
)
from infra.postgresql.models.base import BaseModel
from infra.postgresql.models.mixins.ids import HexUuidIDMixin


class PersonDetailsModel(BaseModel):
    __tablename__ = "knowledge__person_details_model"

    item_id: Mapped[str] = mapped_column(String(length=32), primary_key=True)
    author_username: Mapped[str] = mapped_column(String(length=255))
    last_name: Mapped[str] = mapped_column(String(length=255))
    first_name: Mapped[str] = mapped_column(String(length=255))
    middle_name: Mapped[str] = mapped_column(String(length=255))
    email: Mapped[str] = mapped_column(String(length=320))
    phone: Mapped[str] = mapped_column(String(length=64))
    telegram: Mapped[str] = mapped_column(String(length=255))
    birthday_day: Mapped[int | None] = mapped_column(Integer)
    birthday_month: Mapped[int | None] = mapped_column(Integer)
    birthday_year: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("item_id", "author_username", name="person_details_id_author_uniq"),
        ForeignKeyConstraint(
            ["item_id", "author_username"],
            [
                "knowledge__knowledge_item_model.id",
                "knowledge__knowledge_item_model.author_username",
            ],
            ondelete="CASCADE",
            name="person_details_item_author_fk",
        ),
        CheckConstraint(
            "("
            "birthday_day IS NULL AND birthday_month IS NULL AND birthday_year IS NULL"
            ") OR ("
            "birthday_day IS NOT NULL AND birthday_month IS NOT NULL"
            " AND birthday_day BETWEEN 1 AND 31"
            " AND birthday_month BETWEEN 1 AND 12"
            " AND (birthday_year IS NULL OR birthday_year BETWEEN 1 AND 9999)"
            " AND birthday_day <= CASE"
            " WHEN birthday_month IN (1, 3, 5, 7, 8, 10, 12) THEN 31"
            " WHEN birthday_month IN (4, 6, 9, 11) THEN 30"
            " WHEN birthday_year IS NULL THEN 29"
            " WHEN birthday_year % 400 = 0"
            "   OR (birthday_year % 4 = 0 AND birthday_year % 100 <> 0) THEN 29"
            " ELSE 28 END"
            " AND (birthday_year IS NULL"
            "   OR make_date(birthday_year, birthday_month, birthday_day) <= CURRENT_DATE)"
            ")",
            name="person_details_birthday_check",
        ),
        Index(
            "person_details_author_name_search_idx",
            "author_username",
            func.lower(last_name).label("last_name_lower"),
            func.lower(first_name).label("first_name_lower"),
            "item_id",
        ),
        Index(
            "person_details_author_email_item_idx",
            "author_username",
            func.lower(email).label("email_lower"),
            "item_id",
        ),
        Index(
            "person_details_last_name_trgm_idx",
            func.lower(last_name).label("last_name_lower_trgm"),
            postgresql_using="gin",
            postgresql_ops={"last_name_lower_trgm": "gin_trgm_ops"},
        ),
        Index(
            "person_details_first_name_trgm_idx",
            func.lower(first_name).label("first_name_lower_trgm"),
            postgresql_using="gin",
            postgresql_ops={"first_name_lower_trgm": "gin_trgm_ops"},
        ),
        Index(
            "person_details_middle_name_trgm_idx",
            func.lower(middle_name).label("middle_name_lower_trgm"),
            postgresql_using="gin",
            postgresql_ops={"middle_name_lower_trgm": "gin_trgm_ops"},
        ),
        Index(
            "person_details_email_trgm_idx",
            func.lower(email).label("email_lower_trgm"),
            postgresql_using="gin",
            postgresql_ops={"email_lower_trgm": "gin_trgm_ops"},
        ),
        CheckConstraint(
            "char_length(trim(last_name)) > 0 AND char_length(trim(first_name)) > 0",
            name="person_details_required_names_check",
        ),
    )

    @classmethod
    def from_domain_schema(cls, *, details: PersonDetails, author_username: str) -> Self:
        return cls(
            item_id=details.item_id,
            author_username=author_username,
            last_name=details.last_name,
            first_name=details.first_name,
            middle_name=details.middle_name,
            email=details.email,
            phone=details.phone,
            telegram=details.telegram,
            birthday_day=details.birthday.day if details.birthday is not None else None,
            birthday_month=details.birthday.month if details.birthday is not None else None,
            birthday_year=details.birthday.year if details.birthday is not None else None,
        )

    def to_domain_schema(self) -> PersonDetails:
        birthday = None
        if self.birthday_day is not None and self.birthday_month is not None:
            birthday = PersonBirthday(
                day=self.birthday_day,
                month=self.birthday_month,
                year=self.birthday_year,
            )
        return PersonDetails(
            item_id=self.item_id,
            last_name=self.last_name,
            first_name=self.first_name,
            middle_name=self.middle_name,
            email=self.email,
            phone=self.phone,
            telegram=self.telegram,
            birthday=birthday,
        )


class PersonRelationshipTypeModel(HexUuidIDMixin, AuditMixin, BaseModel):
    __tablename__ = "knowledge__person_relationship_type_model"

    author_username: Mapped[str] = mapped_column(
        String(length=255),
        ForeignKey("auth__user_model.username", ondelete="CASCADE"),
    )
    is_symmetric: Mapped[bool] = mapped_column(Boolean)
    forward_name: Mapped[str] = mapped_column(String(length=255))
    reverse_name: Mapped[str] = mapped_column(String(length=255))

    __table_args__ = (
        UniqueConstraint(
            "id",
            "author_username",
            name="person_relationship_types_id_author_uniq",
        ),
        CheckConstraint(
            "("
            "is_symmetric AND char_length(trim(forward_name)) > 0"
            " AND reverse_name = forward_name"
            ") OR ("
            "NOT is_symmetric AND char_length(trim(forward_name)) > 0"
            " AND char_length(trim(reverse_name)) > 0"
            ")",
            name="person_relationship_types_names_check",
        ),
        Index(
            "person_relationship_types_author_name_id_idx",
            "author_username",
            func.lower(forward_name).label("forward_name_lower"),
            "id",
        ),
    )

    @classmethod
    def from_create_params(cls, *, params: PersonRelationshipTypeCreateParams) -> Self:
        return cls(
            author_username=params.author_username,
            is_symmetric=params.is_symmetric,
            forward_name=params.forward_name,
            reverse_name=params.reverse_name,
        )

    def to_domain_schema(self) -> PersonRelationshipType:
        return PersonRelationshipType(
            id=self.id,
            author_username=self.author_username,
            is_symmetric=self.is_symmetric,
            forward_name=self.forward_name,
            reverse_name=self.reverse_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class PersonRelationshipModel(HexUuidIDMixin, AuditMixin, BaseModel):
    __tablename__ = "knowledge__person_relationship_model"

    author_username: Mapped[str] = mapped_column(String(length=255))
    source_person_id: Mapped[str] = mapped_column(String(length=32))
    target_person_id: Mapped[str] = mapped_column(String(length=32))
    relationship_type_id: Mapped[str] = mapped_column(String(length=32))
    note: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        ForeignKeyConstraint(
            ["source_person_id", "author_username"],
            [
                "knowledge__person_details_model.item_id",
                "knowledge__person_details_model.author_username",
            ],
            ondelete="CASCADE",
            name="person_relationships_source_author_fk",
        ),
        ForeignKeyConstraint(
            ["target_person_id", "author_username"],
            [
                "knowledge__person_details_model.item_id",
                "knowledge__person_details_model.author_username",
            ],
            ondelete="CASCADE",
            name="person_relationships_target_author_fk",
        ),
        ForeignKeyConstraint(
            ["relationship_type_id", "author_username"],
            [
                "knowledge__person_relationship_type_model.id",
                "knowledge__person_relationship_type_model.author_username",
            ],
            ondelete="RESTRICT",
            name="person_relationships_type_author_fk",
        ),
        CheckConstraint(
            "source_person_id <> target_person_id",
            name="person_relationships_not_self_check",
        ),
        Index(
            "person_relationships_author_pair_type_uniq",
            "author_username",
            func.least(source_person_id, target_person_id),
            func.greatest(source_person_id, target_person_id),
            "relationship_type_id",
            unique=True,
        ),
        Index(
            "person_relationships_author_source_idx",
            "author_username",
            "source_person_id",
            "id",
        ),
        Index(
            "person_relationships_author_target_idx",
            "author_username",
            "target_person_id",
            "id",
        ),
        Index(
            "person_relationships_author_type_id_idx",
            "author_username",
            "relationship_type_id",
            "id",
        ),
        CheckConstraint(
            "char_length(note) <= 10000",
            name="person_relationships_note_length_check",
        ),
    )

    def to_domain_schema(
        self,
        *,
        relationship_type: PersonRelationshipType,
    ) -> PersonRelationship:
        return PersonRelationship(
            id=self.id,
            author_username=self.author_username,
            source_person_id=self.source_person_id,
            target_person_id=self.target_person_id,
            relationship_type=relationship_type,
            note=self.note,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
