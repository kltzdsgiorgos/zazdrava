import os
import gzip
import fitparse
import pandas as pd
from django import forms
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import FitRecord


class FitUploadForm(forms.Form):
    file = forms.FileField(label="Upload FIT File")


def handle_fit_file(file_path):
    """Extracts data from FIT file and saves it to the database."""
    fit_data = fitparse.FitFile(file_path)
    data = []
    for record in fit_data.get_messages("record"):
        record_data = {}
        for field in record:
            if field.name and field.value is not None:
                record_data[field.name] = field.value
        data.append(record_data)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save records to database
    FitRecord.objects.bulk_create(
        [FitRecord(**row) for row in df.to_dict(orient="records")]
    )


def upload_fit_file(request):
    """Handles file upload and data extraction."""
    if request.method == "POST":
        form = FitUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            file_path = default_storage.save(
                f"fit_files/{uploaded_file.name}", ContentFile(uploaded_file.read())
            )

            # Decompress GZ file
            if uploaded_file.name.endswith(".gz"):
                decompressed_path = file_path.replace(".gz", "")
                with gzip.open(default_storage.path(file_path), "rb") as f_in, open(
                    default_storage.path(decompressed_path), "wb"
                ) as f_out:
                    f_out.write(f_in.read())
                os.remove(default_storage.path(file_path))
                file_path = decompressed_path

            # Parse and save data
            handle_fit_file(default_storage.path(file_path))

            return redirect("fit_data_view")
    else:
        form = FitUploadForm()
    return render(request, "upload.html", {"form": form})


def fit_data_view(request):
    """Displays stored FIT records."""
    records = FitRecord.objects.all()
    return render(request, "fit_data.html", {"records": records})
