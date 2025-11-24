from django.urls import include, path

from .sewer import urls as sewer_urls

app_name = "sewer"

urlpatterns = [
    path("sewer/", include(sewer_urls)),
]
