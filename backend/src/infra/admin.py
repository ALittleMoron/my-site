from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from import_export.admin import ImportExportModelAdmin
from mdeditor.widgets import MDEditorWidget
from unfold.admin import ModelAdmin, display
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from db.models import CompetencyMatrixItemModel, ResourceModel
from infra.forms import CompetencyMatrixItemForm

if TYPE_CHECKING:
    from django.db.models import QuerySet


@admin.register(ResourceModel)
class ResourceAdmin(ModelAdmin):
    search_fields = ["name"]


@admin.register(CompetencyMatrixItemModel)
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
        "status",
        "status_changed",
    ]
    list_display = [
        "id",
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
    ) -> "QuerySet[CompetencyMatrixItemModel, CompetencyMatrixItemModel]":
        qs = super().get_queryset(request)
        return qs.prefetch_related("resources")  # type: ignore[no-any-return]

    @display(description="Вопрос")  # type: ignore[misc]
    def display_question(self, instance: CompetencyMatrixItemModel) -> str:
        return instance.question

    @display(description="Лист")  # type: ignore[misc]
    def display_sheet(self, instance: CompetencyMatrixItemModel) -> str:
        return instance.sheet

    @display(description="Раздел")  # type: ignore[misc]
    def display_section(self, instance: CompetencyMatrixItemModel) -> str:
        return instance.section if instance.subsection else ""

    @display(description="Подраздел")  # type: ignore[misc]
    def display_subsection(self, instance: CompetencyMatrixItemModel) -> str:
        return instance.subsection if instance.subsection else ""

    @display(description="Уровень компетенций")  # type: ignore[misc]
    def display_grade(self, instance: CompetencyMatrixItemModel) -> str:
        return instance.grade if instance.grade else ""
