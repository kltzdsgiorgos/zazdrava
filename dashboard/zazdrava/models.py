from django.db import models


class Workout(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FitRecord(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
        return f"{self.timestamp} - {self.workout.name}"
