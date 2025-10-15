from django.urls import path, include
from .order import urls as order_urls

app_name = "order"

urlpatterns = [
    path('order/', include(order_urls)),
]