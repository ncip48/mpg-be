from django.urls import include, path

from .sewer import urls as sewer_urls
from .sewer_distribution import urls as sewer_distribution_urls

app_name = "sewer"

urlpatterns = [
    path("sewer/", include(sewer_urls)),
    path("sewer/", include(sewer_distribution_urls)),
]
