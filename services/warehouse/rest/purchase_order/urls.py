from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PurchaseOrderViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
