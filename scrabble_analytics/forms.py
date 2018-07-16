from django import forms
from django.core.exceptions import ValidationError

class SubmitLettersForm(forms.Form):
    list_letters = forms.CharField(label='', widget=forms.TextInput(attrs={"placeholder":"List of letters (use _ if blank)*", "class":"form-control"}), required=True)
    
    def clean(self):
        super(SubmitLettersForm, self).clean()


