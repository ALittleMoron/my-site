from django.db import models
from mdeditor.fields import MDTextField

from admin.core.models import TypeModel


class Section(TypeModel):
    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"


class SubSection(TypeModel):
    class Meta:
        verbose_name = "Подраздел"
        verbose_name_plural = "Подразделы"


class Grade(TypeModel):
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

    def __str__(self) -> str:
        return f'Внешний ресурс "{self.name}"'

    class Meta:
        verbose_name = "Внешние ресурс"
        verbose_name_plural = "Внешние ресурсы"


class CompetencyMatrixItem(models.Model):
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

    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    subsection = models.ForeignKey(
        SubSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    resources = models.ManyToManyField(
        Resource,
        verbose_name="Внешние ресурсы",
        blank=True,
    )

    def __str__(self) -> str:
        return self.question

    class Meta:
        db_table = "competency_matrix_item"
        ordering = ['section', 'subsection', 'grade', 'question']
        verbose_name = "Элемент матрицы компетенций"
        verbose_name_plural = "Элементы матрицы компетенций"
