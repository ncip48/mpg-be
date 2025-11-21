from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QCLineVerificationViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(
    r"qc-line-verifications", QCLineVerificationViewSet, basename="qc-line-verification"
)
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
