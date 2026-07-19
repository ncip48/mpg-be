from django.urls import include, path

from .reject import urls as reject_urls

app_name = "defect"

urlpatterns = [
    path("defect/", include(reject_urls)),
]
