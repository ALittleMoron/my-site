from django import forms

from db.models import CompetencyMatrixItem


class CompetencyMatrixItemForm(forms.ModelForm):
    class Meta:
        model = CompetencyMatrixItem
        fields = "__all__"  # noqa: DJ007
