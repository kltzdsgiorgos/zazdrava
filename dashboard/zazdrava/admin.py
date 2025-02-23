from django.contrib import admin
from .models import FitRecord


def fit_record_display(obj):
    return obj.data


@admin.register(FitRecord)
class FitRecordAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "get_data_fields")

    def get_data_fields(self, obj):
        return (
            ", ".join([f"{k}: {v}" for k, v in obj.data.items()])
            if obj.data
            else "No Data"
        )

    get_data_fields.short_description = "FIT Data"
