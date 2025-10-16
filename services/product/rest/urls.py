from django.urls import path, include
from .product import urls as product_urls
from .variant_type import urls as product_variant_type_urls
from .fabric_type import urls as fabric_type_urls

app_name = "product"

urlpatterns = [
    path('product/', include(product_urls)),
    path('product/', include(product_variant_type_urls)),
    path('product/', include(fabric_type_urls)),
]