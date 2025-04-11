from typing import Any, Self

from django.db import models
from django.db.models import functions as func
from mdeditor.fields import MDTextField
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField

from core.competency_matrix.enums import StatusEnum
from core.competency_matrix.schemas import CompetencyMatrixItem, Resource, Resources


class DraftManager(models.Manager):
    def get_queryset(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        return super().get_queryset().filter(status="draft")


class PublishedManager(models.Manager):
    def get_queryset(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        return super().get_queryset().filter(status="published")


class PublishModel(models.Model):
    STATUS = Choices("draft", "published")
    status = StatusField(verbose_name="Статус")
    status_changed = MonitorField(verbose_name="Статус изменен", monitor="status")

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        update_fields = kwargs.get("update_fields")
        if update_fields and "status" in update_fields:
            kwargs["update_fields"] = set(update_fields).union({"status_changed"})

        super().save(*args, **kwargs)


class ResourceModel(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
        null=False,
        blank=False,
    )
    url = models.URLField(
        verbose_name="Ссылка",
        null=False,
        blank=False,
    )
    context = MDTextField(
        verbose_name="Контекст, зачем этот ресурс был сюда добавлен",
        null=False,
        blank=True,
    )

    class Meta:
        db_table = "competency_matrix_resources"
        verbose_name = "Внешние ресурс"
        verbose_name_plural = "Внешние ресурсы"

    def __str__(self) -> str:
        return f'Внешний ресурс "{self.name}"'

    @classmethod
    def from_domain_schema(cls, schema: Resource) -> Self:
        return cls(
            name=schema.name,
            url=schema.url,
            context=schema.context,
        )

    def to_domain_schema(self) -> Resource:
        return Resource(
            id=self.id,
            name=self.name,
            url=self.url,
            context=self.context,
        )


class CompetencyMatrixItemModel(PublishModel, models.Model):
    objects: "models.Manager[CompetencyMatrixItemModel]" = models.Manager()
    draft: "models.Manager[CompetencyMatrixItemModel]" = DraftManager()
    published: "models.Manager[CompetencyMatrixItemModel]" = PublishedManager()

    question = models.CharField(
        max_length=255,
        verbose_name="Вопрос",
        null=False,
        blank=False,
    )
    answer = MDTextField(
        verbose_name="Ответ",
        null=False,
        blank=True,
    )
    interview_expected_answer = MDTextField(
        verbose_name="Ответ, который ожидают на интервью",
        null=False,
        blank=True,
    )
    sheet = models.CharField(
        max_length=255,
        verbose_name="Лист",
        null=False,
        blank=False,
    )
    section = models.CharField(
        max_length=255,
        verbose_name="Раздел",
        null=False,
        blank=True,
    )
    subsection = models.CharField(
        max_length=255,
        verbose_name="Подраздел",
        null=False,
        blank=True,
    )
    grade = models.CharField(
        max_length=255,
        verbose_name="Уровень компетенции",
        null=False,
        blank=True,
    )
    resources = models.ManyToManyField(
        ResourceModel,
        verbose_name="Внешние ресурсы",
        blank=True,
    )

    class Meta:
        db_table = "competency_matrix_item"
        indexes = [
            models.Index(func.Lower("sheet"), name="cmi_sheet_idx"),
        ]
        ordering = ["subsection", "section", "grade", "question"]
        verbose_name = "Элемент матрицы компетенций"
        verbose_name_plural = "Элементы матрицы компетенций"

    def __str__(self) -> str:
        return f"[{self.section} - {self.subsection}] {self.question}"

    @classmethod
    def from_domain_schema(cls, item: CompetencyMatrixItem) -> Self:
        return cls(
            pk=item.id,
            question=item.question,
            answer=item.answer,
            status=item.status,
            status_changed=item.status_changed,
            interview_expected_answer=item.interview_expected_answer,
            sheet=item.sheet,
            section=item.section,
            subsection=item.subsection,
            grade=item.grade,
        )

    def to_domain_schema(self) -> CompetencyMatrixItem:
        return CompetencyMatrixItem(
            id=self.pk,
            question=self.question,
            answer=self.answer,
            status=StatusEnum(self.status),
            status_changed=self.status_changed,
            interview_expected_answer=self.interview_expected_answer,
            sheet=self.sheet,
            section=self.section,
            subsection=self.subsection,
            grade=self.grade,
            resources=Resources(
                values=[resource.to_domain_schema() for resource in self.resources.all()],
            ),
        )
