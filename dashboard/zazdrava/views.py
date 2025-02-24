import os
import gzip
import fitparse
import pandas as pd
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import path
import plotly.express as px
import plotly.io as pio
from .models import FitRecord
from .forms import FitUploadForm
from .models import Workout, FitRecord


def handle_fit_file(file_path, workout_name):
    """Extracts data from FIT file and saves it to the database under a workout."""
    fit_data = fitparse.FitFile(file_path)
    records = []

    # Ensure Workout exists
    workout, created = Workout.objects.get_or_create(name=workout_name)

    for record in fit_data.get_messages("record"):
        record_data = {}
        timestamp = None

        for field in record:
            if field.name and field.value is not None:
                if field.name == "timestamp":
                    timestamp = field.value
                else:
                    record_data[field.name] = field.value

        if timestamp:
            records.append(
                FitRecord(workout=workout, timestamp=timestamp, data=record_data)
            )

    FitRecord.objects.bulk_create(records)


def upload_fit_file(request):
    if request.method == "POST":
        form = FitUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            workout_name = uploaded_file.name  # Use filename as workout name

            file_path = default_storage.save(
                f"fit_files/{uploaded_file.name}", ContentFile(uploaded_file.read())
            )

            if uploaded_file.name.endswith(".gz"):
                decompressed_path = file_path.replace(".gz", "")
                with gzip.open(default_storage.path(file_path), "rb") as f_in, open(
                    default_storage.path(decompressed_path), "wb"
                ) as f_out:
                    f_out.write(f_in.read())
                os.remove(default_storage.path(file_path))
                file_path = decompressed_path

            handle_fit_file(default_storage.path(file_path), workout_name)

            return redirect("fit_data_view")
    else:
        form = FitUploadForm()
    return render(request, "zazdrava/upload.html", {"form": form})


def fit_data_view(request):
    """Display only the workout chart."""
    workouts = Workout.objects.prefetch_related("fit_records").all()

    if not workouts.exists():
        return render(
            request,
            "zazdrava/fit_data.html",
            {"charts": "<p>No workout data available.</p>"},
        )

    # Process data
    data = []
    for workout in workouts:
        for record in workout.fit_records.all():  # ✅ Corrected attribute access
            data.append(
                {
                    "timestamp": record.timestamp,
                    "speed": record.data.get("speed", 0),
                    "workout": workout.name,
                }
            )

    df = pd.DataFrame(data)

    # Create the Plotly chart
    fig = px.line(
        df, x="timestamp", y="speed", color="workout", title="Workout Speed Over Time"
    )
    chart_html = fig.to_html(full_html=False)

    return render(request, "zazdrava/fit_data.html", {"charts": chart_html})
