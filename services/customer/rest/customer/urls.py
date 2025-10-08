from django.urls import path, include
from .views import CustomerViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='printer')
# --- End Router ---

urlpatterns = [
    path('', include(router.urls)),
    path(
        "autocomplete/",
        CustomerViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete"
    ),
]