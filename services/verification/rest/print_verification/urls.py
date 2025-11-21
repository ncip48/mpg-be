from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrintVerificationViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"print-verifications", PrintVerificationViewSet, basename="print-verification"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
