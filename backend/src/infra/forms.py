from django import forms

from db.models import CompetencyMatrixItemModel


class CompetencyMatrixItemForm(forms.ModelForm):
    class Meta:
        model = CompetencyMatrixItemModel
        fields = "__all__"  # noqa: DJ007
