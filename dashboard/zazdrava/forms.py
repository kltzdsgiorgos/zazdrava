from django import forms


class FitUploadForm(forms.Form):
    file = forms.FileField(label="Upload FIT File")
