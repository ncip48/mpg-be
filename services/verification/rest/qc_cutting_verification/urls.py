from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QCCuttingVerificationViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"qc-cutting-verifications",
    QCCuttingVerificationViewSet,
    basename="qc-cutting-verification",
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
