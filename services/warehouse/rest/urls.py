from django.urls import include, path

from .warehouse_receipt import urls as warehouse_receipt_urls

app_name = "warehouse"

urlpatterns = [
    path("warehouse/", include(warehouse_receipt_urls)),
]
