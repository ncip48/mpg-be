from django.urls import include, path

from .order import urls as tracking_order_urls

app_name = "tracking"

urlpatterns = [
    path("tracking/", include(tracking_order_urls)),
]
