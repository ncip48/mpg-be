from django.urls import include, path

from .forecast import urls as forecast_urls

app_name = "forecast"

urlpatterns = [
    path("forecast/", include(forecast_urls)),
]
