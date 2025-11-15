from django.urls import include, path

from .order import urls as order_urls
from .order_item import urls as order_item_urls

app_name = "order"

urlpatterns = [
    path("order/", include(order_urls)),
    path("order/", include(order_item_urls)),
]
