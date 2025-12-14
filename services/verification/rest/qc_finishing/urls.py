from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QCFinishingViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"qc-finishing-verifications", QCFinishingViewSet, basename="qc-finishing"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
