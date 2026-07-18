from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QCPressVerificationViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"qc-press-verifications", QCPressVerificationViewSet, basename="qc-press-verification"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
