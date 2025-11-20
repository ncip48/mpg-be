from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ForecastViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"forecasts", ForecastViewSet, basename="forecast")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
