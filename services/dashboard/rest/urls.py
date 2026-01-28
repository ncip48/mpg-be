from django.urls import path, include
from .dashboard import urls as dashboard_urls

app_name = "dashboard"

urlpatterns = [
    path("dashboard/", include(dashboard_urls)),
]
