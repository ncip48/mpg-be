from django.urls import path, include
from .views import OrderViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="orders")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
