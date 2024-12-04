from django.contrib import admin
from django.db import models
from mdeditor.widgets import MDEditorWidget
from unfold.admin import ModelAdmin, display

from .forms import CompetencyMatrixItemForm
from .models import CompetencyMatrixItem, Grade, Resource, Section, SubSection


@admin.register(Section)
class SectionAdmin(ModelAdmin): ...


@admin.register(SubSection)
class SubSectionAdmin(ModelAdmin): ...


@admin.register(Grade)
class GradeAdmin(ModelAdmin): ...


@admin.register(Resource)
class ResourceAdmin(ModelAdmin):
    search_fields = ['name']


@admin.register(CompetencyMatrixItem)
class CompetencyMatrixElementAdmin(ModelAdmin):
    form = CompetencyMatrixItemForm
    warn_unsaved_form = True
    compressed_fields = True
    list_filter_submit = True
    list_filter_sheet = False
    list_fullwidth = True
    list_display = [
        'id',
        "display_question",
        "display_section",
        "display_subsection",
        "display_grade",
    ]
    autocomplete_fields = [
        "resources",
    ]
    formfield_overrides = {
        models.TextField: {"widget": MDEditorWidget},
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("section", "subsection", "grade").prefetch_related("resources")

    @display(description="Вопрос")
    def display_question(self, instance: CompetencyMatrixItem) -> str:
        return instance.question

    @display(description="Раздел")
    def display_section(self, instance: CompetencyMatrixItem) -> str:
        return instance.section.name if instance.section else ""

    @display(description="Подраздел")
    def display_subsection(self, instance: CompetencyMatrixItem) -> str:
        return instance.subsection.name if instance.subsection else ""

    @display(description="Уровень компетенций")
    def display_grade(self, instance: CompetencyMatrixItem) -> str:
        return instance.grade.name if instance.grade else ""
