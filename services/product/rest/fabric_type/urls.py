from django.urls import path, include
from .views import FabricTypeViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'fabric-types', FabricTypeViewSet, basename='fabric-type')
# --- End Router ---

urlpatterns = [
    path(
        "fabric-types/autocomplete/",
        FabricTypeViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete-fabric-type"
    ),
    path('', include(router.urls)),
]