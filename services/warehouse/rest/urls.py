from django.urls import include, path

from .issuing import urls as issuing_urls
from .material import urls as material_urls
from .purchase_order import urls as po_urls
from .receiving import urls as receiving_urls
from .stock_opname import urls as so_urls
from .supplier import urls as supplier_urls
from .warehouse_delivery import urls as warehouse_delivery_urls
from .warehouse_receipt import urls as warehouse_receipt_urls

app_name = "warehouse"

urlpatterns = [
    path("warehouse/", include(warehouse_delivery_urls)),
    path("warehouse/", include(warehouse_receipt_urls)),
    path("warehouse/", include(supplier_urls)),
    path("warehouse/", include(material_urls)),
    path("warehouse/", include(po_urls)),
    path("warehouse/", include(so_urls)),
    path("warehouse/", include(receiving_urls)),
    path("warehouse/", include(issuing_urls)),
]
