import os
import gzip
import fitparse
import pandas as pd
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import FitRecord, Workout
from .forms import FitUploadForm
import json
from django.shortcuts import get_object_or_404


def handle_fit_file(file_path, workout_name):
    """Extracts data from FIT file and saves it as a workout."""
    fit_data = fitparse.FitFile(file_path)
    workout = Workout.objects.create(name=workout_name)
    records = []

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
    """Handles file upload and creates a workout for it."""
    if request.method == "POST":
        form = FitUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            workout_name = uploaded_file.name  # Name the workout after the file
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
    return render(request, "upload.html", {"form": form})


def workout_detail(request, workout_id):
    """Displays details of a single workout, including a graph."""
    workout = get_object_or_404(Workout, id=workout_id)

    # Extract timestamp and key metrics (Modify based on your data)
    records = workout.records.all().order_by("timestamp")
    timestamps = [record.timestamp.strftime("%Y-%m-%d %H:%M:%S") for record in records]
    altitude = [record.data.get("altitude", 0) for record in records]
    heart_rate = [record.data.get("heart_rate", 0) for record in records]
    speed = [record.data.get("enhanced_speed", 0) for record in records]

    return render(
        request,
        "workout_detail.html",
        {
            "workout": workout,
            "timestamps": json.dumps(timestamps),
            "altitude": json.dumps(altitude),
            "heart_rate": json.dumps(heart_rate),
            "speed": json.dumps(speed),
        },
    )


def fit_data_view(request):
    """Displays workouts instead of individual records."""
    workouts = Workout.objects.prefetch_related("records").all()
    # print(workouts.count())
    for data in workouts:
        # print(data.records.count())
        for record in data.records.all():
            print(record.data)
    return render(request, "fit_data.html", {"workouts": workouts})
