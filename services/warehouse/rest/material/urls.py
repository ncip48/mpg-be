from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MaterialViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"materials", MaterialViewSet, basename="material")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
