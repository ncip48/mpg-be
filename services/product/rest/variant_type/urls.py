from django.urls import path, include
from .views import ProductVariantTypeViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'variant-types', ProductVariantTypeViewSet, basename='product-variant-type')
# --- End Router ---

urlpatterns = [
    path(
        "variant-types/autocomplete/",
        ProductVariantTypeViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete-variant-type"
    ),
    path('', include(router.urls)),
]