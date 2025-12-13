from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SewerDistributionViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"sewer-distributions", SewerDistributionViewSet, basename="sewer-distribution"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
