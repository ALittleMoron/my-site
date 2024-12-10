from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from import_export.admin import ImportExportModelAdmin
from mdeditor.widgets import MDEditorWidget
from unfold.admin import ModelAdmin, display
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .forms import CompetencyMatrixItemForm
from .models import CompetencyMatrixItem, Grade, Resource, Section, Sheet, SubSection

if TYPE_CHECKING:
    from django.db.models import QuerySet


@admin.register(Sheet)
class SheetAdmin(ModelAdmin):
    search_fields = ['name']


@admin.register(Section)
class SectionAdmin(ModelAdmin):
    search_fields = ['name']


@admin.register(SubSection)
class SubSectionAdmin(ModelAdmin):
    search_fields = ['name']


@admin.register(Grade)
class GradeAdmin(ModelAdmin):
    search_fields = ['name']


@admin.register(Resource)
class ResourceAdmin(ModelAdmin):
    search_fields = ['name']


@admin.register(CompetencyMatrixItem)
class CompetencyMatrixElementAdmin(ModelAdmin, ImportExportModelAdmin):
    form = CompetencyMatrixItemForm
    import_form_class = ImportForm
    export_form_class = ExportForm
    warn_unsaved_form = True
    compressed_fields = True
    list_filter_submit = True
    list_filter_sheet = False
    list_fullwidth = True
    readonly_fields = [
        'status',
        'status_changed',
    ]
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

    def get_queryset(
        self,
        request: HttpRequest,
    ) -> "QuerySet[CompetencyMatrixItem, CompetencyMatrixItem]":
        qs = super().get_queryset(request)
        return qs.select_related(  # type: ignore[no-any-return]
            "subsection",
            "subsection__section",
            "subsection__section__sheet",
            "grade",
        ).prefetch_related("resources")

    @display(description="Вопрос")  # type: ignore[misc]
    def display_question(self, instance: CompetencyMatrixItem) -> str:
        return instance.question

    @display(description="Раздел")  # type: ignore[misc]
    def display_section(self, instance: CompetencyMatrixItem) -> str:
        return instance.subsection.section.name if instance.subsection else ""

    @display(description="Подраздел")  # type: ignore[misc]
    def display_subsection(self, instance: CompetencyMatrixItem) -> str:
        return instance.subsection.name if instance.subsection else ""

    @display(description="Уровень компетенций")  # type: ignore[misc]
    def display_grade(self, instance: CompetencyMatrixItem) -> str:
        return instance.grade.name if instance.grade else ""
