from django.db import models


class Workout(models.Model):
    name = models.CharField(max_length=255)  # e.g., "Morning Run"
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FitRecord(models.Model):
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="fit_records"
    )
    timestamp = models.DateTimeField()
    data = models.JSONField()  # Stores speed, altitude, etc.

    def __str__(self):
        return f"Record at {self.timestamp}"
