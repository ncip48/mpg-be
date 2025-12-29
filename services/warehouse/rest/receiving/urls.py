from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReceivingViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"receiving", ReceivingViewSet, basename="receiving")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
