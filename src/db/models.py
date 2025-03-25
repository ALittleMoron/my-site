from typing import Any

from django.db import models
from django.db.models import functions as func
from mdeditor.fields import MDTextField
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField


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


class Resource(models.Model):
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
        verbose_name = "Внешние ресурс"
        verbose_name_plural = "Внешние ресурсы"

    def __str__(self) -> str:
        return f'Внешний ресурс "{self.name}"'


class CompetencyMatrixItem(PublishModel, models.Model):
    draft: "models.Manager[CompetencyMatrixItem]"
    published: "models.Manager[CompetencyMatrixItem]"

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
        Resource,
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
