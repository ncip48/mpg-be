from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RejectViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"rejects", RejectViewSet, basename="rejects")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
