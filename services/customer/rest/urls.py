from django.urls import path, include
from .customer import urls as customer_urls

app_name = "customer"

urlpatterns = [
    path('customer/', include(customer_urls)),
]