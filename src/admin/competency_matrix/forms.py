from django import forms

from .models import CompetencyMatrixItem


class CompetencyMatrixItemForm(forms.ModelForm):
    class Meta:
        model = CompetencyMatrixItem
        fields = "__all__"  # noqa: DJ007
