from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SewerViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"sewers", SewerViewSet, basename="sewer")
# --- End Router ---

urlpatterns = [
    path(
        "sewers/autocomplete/",
        SewerViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete",
    ),
    path("", include(router.urls)),
]
