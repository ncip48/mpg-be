from django.urls import include, path

from .complaint import urls as complaint_urls

app_name = "ticket"

urlpatterns = [
    path("ticket/", include(complaint_urls)),
]
