from django import forms
from .models import apiURL


class apiURLForm(forms.ModelForm):
    class Meta:
        model = apiURL
        fields = ["url1", "url2", "url3"]

