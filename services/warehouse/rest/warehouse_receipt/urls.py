from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WarehouseReceiptViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"warehouse-receipts", WarehouseReceiptViewSet, basename="warehouse-receipt"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
