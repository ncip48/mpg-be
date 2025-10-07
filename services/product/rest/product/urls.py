from django.urls import path, include
from .views import ProductViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
# --- End Router ---

urlpatterns = [
    path('', include(router.urls)),
    path(
        "autocomplete/",
        ProductViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete"
    ),
]