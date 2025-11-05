from django.urls import path, include
from .deposit import urls as deposit_urls

app_name = "deposit"

urlpatterns = [
    path("deposit/", include(deposit_urls)),
]
