from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SupplierViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
