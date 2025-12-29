from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IssuingViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"issuing", IssuingViewSet, basename="issuing")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
