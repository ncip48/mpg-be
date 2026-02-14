from django.urls import path, include
from .views import ModuleViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"modules", ModuleViewSet, basename="module")
# --- End Router ---

urlpatterns = [
    path(
        "modules/autocomplete/",
        ModuleViewSet.as_view({"get": "autocomplete"}),
        name="module-autocomplete",
    ),
    path("", include(router.urls)),
]
