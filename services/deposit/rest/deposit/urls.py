from django.urls import path, include
from .views import DepositViewSet
from rest_framework.routers import DefaultRouter

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"deposits", DepositViewSet, basename="deposits")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
    path(
        "deposits/<str:subid>/invoice/",
        DepositViewSet.as_view({"get": "generate_invoice_pdf"}),
        name="invoice-pdf",
    ),
]
