from django.db import models


class Workout(models.Model):
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.uploaded_at}"


class FitRecord(models.Model):
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="records"
    )
    timestamp = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
        return f"Record at {self.timestamp} ({self.workout.name})"
