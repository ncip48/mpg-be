from django.urls import path, include
from .printer import urls as printer_urls

app_name = "printer"

urlpatterns = [
    path('printer/', include(printer_urls)),
]