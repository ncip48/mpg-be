from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WarehouseDeliveryViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"warehouse-deliveries", WarehouseDeliveryViewSet, basename="warehouse-delivery"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
