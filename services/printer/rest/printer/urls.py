from django.urls import path, include
from .views import PrinterViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r'printers', PrinterViewSet, basename='printer')
# --- End Router ---

urlpatterns = [
    path(
        "printers/autocomplete/",
        PrinterViewSet.as_view({"get": "autocomplete"}),
        name="autocomplete"
    ),
    path('', include(router.urls)),
]