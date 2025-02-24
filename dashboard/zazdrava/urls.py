from django.urls import path
from .views import upload_fit_file, fit_data_view

urlpatterns = [
    path("upload/", upload_fit_file, name="upload_fit_file"),
    path("data/", fit_data_view, name="fit_data_view"),
]
