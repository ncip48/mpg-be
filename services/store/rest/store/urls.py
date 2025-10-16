from django.urls import path, include
from .views import StoreViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
# --- End Router ---

urlpatterns = [
    path(
        "stores/autocomplete/",
        StoreViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete"
    ),
    path('', include(router.urls)),
]