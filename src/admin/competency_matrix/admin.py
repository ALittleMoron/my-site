from django.contrib import admin
from django.db import models
from mdeditor.widgets import MDEditorWidget
from unfold.admin import ModelAdmin, display

from .forms import CompetencyMatrixItemForm
from .models import CompetencyMatrixItem, SubSection, Section, Grade, Resource


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
    list_display = ['id', "display_question"]
    autocomplete_fields = ["resources"]
    formfield_overrides = {models.TextField: {"widget": MDEditorWidget}}

    @display(description="Вопрос")
    def display_question(self, instance: CompetencyMatrixItem) -> str:
        return instance.question
