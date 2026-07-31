from typing import Self

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    and_,
    case,
    column,
    func,
    or_,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.knowledge.dates.schemas import (
    KnowledgeDateDetails,
    KnowledgeDatePersonLink,
    KnowledgeDateValue,
)
from infra.postgresql.models.base import BaseModel


class KnowledgeDateDetailsModel(BaseModel):
    __tablename__ = "knowledge__date_details_model"

    item_id: Mapped[str] = mapped_column(String(length=32), primary_key=True)
    author_username: Mapped[str] = mapped_column(String(length=255))
    day: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("item_id", "author_username", name="date_details_id_author_uniq"),
        ForeignKeyConstraint(
            ["item_id", "author_username"],
            [
                "knowledge__knowledge_item_model.id",
                "knowledge__knowledge_item_model.author_username",
            ],
            ondelete="CASCADE",
            name="date_details_item_author_fk",
        ),
        CheckConstraint(
            and_(
                column("day").between(1, 31),
                column("month").between(1, 12),
                or_(column("year").is_(None), column("year").between(1, 9999)),
                column("day")
                <= case(
                    (column("month").in_((1, 3, 5, 7, 8, 10, 12)), 31),
                    (column("month").in_((4, 6, 9, 11)), 30),
                    (column("year").is_(None), 29),
                    (
                        or_(
                            column("year") % 400 == 0,
                            and_(
                                column("year") % 4 == 0,
                                column("year") % 100 != 0,
                            ),
                        ),
                        29,
                    ),
                    else_=28,
                ),
                or_(
                    column("year").is_(None),
                    func.make_date(
                        column("year"),
                        column("month"),
                        column("day"),
                    )
                    <= func.current_date(),
                ),
            ),
            name="date_details_calendar_check",
        ),
        Index(
            "date_details_author_calendar_item_idx",
            "author_username",
            "month",
            "day",
            "item_id",
        ),
    )

    @classmethod
    def from_domain_schema(
        cls,
        *,
        details: KnowledgeDateDetails,
        author_username: str,
    ) -> Self:
        return cls(
            item_id=details.item_id,
            author_username=author_username,
            day=details.date.day,
            month=details.date.month,
            year=details.date.year,
        )

    def to_domain_schema(self) -> KnowledgeDateDetails:
        return KnowledgeDateDetails(
            item_id=self.item_id,
            date=KnowledgeDateValue(day=self.day, month=self.month, year=self.year),
        )


class KnowledgeDatePersonModel(BaseModel):
    __tablename__ = "knowledge__date_person_model"

    date_item_id: Mapped[str] = mapped_column(String(length=32))
    person_item_id: Mapped[str] = mapped_column(String(length=32))
    author_username: Mapped[str] = mapped_column(String(length=255))

    __table_args__ = (
        PrimaryKeyConstraint("date_item_id", "person_item_id"),
        ForeignKeyConstraint(
            ["date_item_id", "author_username"],
            [
                "knowledge__date_details_model.item_id",
                "knowledge__date_details_model.author_username",
            ],
            ondelete="CASCADE",
            name="date_people_date_author_fk",
        ),
        ForeignKeyConstraint(
            ["person_item_id", "author_username"],
            [
                "knowledge__person_details_model.item_id",
                "knowledge__person_details_model.author_username",
            ],
            ondelete="CASCADE",
            name="date_people_person_author_fk",
        ),
        Index(
            "date_people_author_person_date_idx",
            "author_username",
            "person_item_id",
            "date_item_id",
        ),
        Index(
            "date_people_author_date_person_idx",
            "author_username",
            "date_item_id",
            "person_item_id",
        ),
    )

    def to_domain_schema(self) -> KnowledgeDatePersonLink:
        return KnowledgeDatePersonLink(
            date_id=self.date_item_id,
            person_id=self.person_item_id,
        )
