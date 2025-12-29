from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StockOpnameViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"stock-opname", StockOpnameViewSet, basename="stock-opname")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
