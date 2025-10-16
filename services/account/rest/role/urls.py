from django.urls import path, include
from .views import RoleViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
# --- End Router ---

urlpatterns = [
    path(
        "roles/autocomplete/",
        RoleViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete"
    ),
    path('', include(router.urls)),
]