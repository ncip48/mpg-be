from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QCFinishingDefectViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"qc-finishing-defects", QCFinishingDefectViewSet, basename="qc-finishing-defect"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
