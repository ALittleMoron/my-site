from django.db import models
from mdeditor.fields import MDTextField

from admin.core.models import ModelWithName, PublishModel


class Sheet(ModelWithName):
    class Meta:
        verbose_name = "Лист"
        verbose_name_plural = "Листы"


class Section(ModelWithName):
    sheet = models.ForeignKey(
        Sheet,
        on_delete=models.CASCADE,
        verbose_name="Лист",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"


class SubSection(ModelWithName):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        verbose_name="Раздел",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Подраздел"
        verbose_name_plural = "Подразделы"


class Grade(ModelWithName):
    class Meta:
        verbose_name = "Уровень компетенции"
        verbose_name_plural = "Уровень компетенций"


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
        verbose_name='Вопрос',
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

    subsection = models.ForeignKey(
        SubSection,
        on_delete=models.SET_NULL,
        verbose_name="Подраздел",
        null=True,
        blank=True,
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        verbose_name="Уровень компетенции",
        null=True,
        blank=True,
    )
    resources = models.ManyToManyField(
        Resource,
        verbose_name="Внешние ресурсы",
        blank=True,
    )

    class Meta:
        db_table = "competency_matrix_item"
        ordering = ['subsection', 'subsection__section', 'grade', 'question']
        verbose_name = "Элемент матрицы компетенций"
        verbose_name_plural = "Элементы матрицы компетенций"

    def __str__(self) -> str:
        return self.question
