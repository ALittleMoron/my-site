# Generated by Django 5.1.3 on 2024-12-03 12:12

import django.db.models.deletion
import mdeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Уровень компетенции',
                'verbose_name_plural': 'Уровень компетенций',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('url', models.URLField(verbose_name='Ссылка')),
                (
                    'context',
                    mdeditor.fields.MDTextField(
                        blank=True, verbose_name='Контекст, зачем этот ресурс был сюда добавлен'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Внешние ресурс',
                'verbose_name_plural': 'Внешние ресурсы',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Раздел',
                'verbose_name_plural': 'Разделы',
            },
        ),
        migrations.CreateModel(
            name='SubSection',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Подраздел',
                'verbose_name_plural': 'Подразделы',
            },
        ),
        migrations.CreateModel(
            name='CompetencyMatrixItem',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('question', models.CharField(max_length=255, verbose_name='Вопрос')),
                ('answer', mdeditor.fields.MDTextField(blank=True, verbose_name='Ответ')),
                (
                    'interview_expected_answer',
                    mdeditor.fields.MDTextField(
                        blank=True, verbose_name='Ответ, который ожидают на интервью'
                    ),
                ),
                (
                    'grade',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='competency_matrix.grade',
                    ),
                ),
                (
                    'resources',
                    models.ManyToManyField(
                        blank=True, to='competency_matrix.resource', verbose_name='Внешние ресурсы'
                    ),
                ),
                (
                    'section',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='competency_matrix.section',
                    ),
                ),
                (
                    'subsection',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='competency_matrix.subsection',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Элемент матрицы компетенций',
                'verbose_name_plural': 'Элементы матрицы компетенций',
                'db_table': 'competency_matrix_item',
                'ordering': ['section', 'subsection', 'grade', 'question'],
            },
        ),
    ]
