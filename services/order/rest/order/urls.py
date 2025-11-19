from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="orders")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
    path(
        "orders/<str:subid>/order-form/",
        OrderViewSet.as_view(
            {
                "get": "order_form",
                "post": "create_order_form",
                "put": "update_order_form",
                "patch": "partial_update_order_form",
                "delete": "delete_order_form",
            }
        ),
        name="order-form-marketplace",
    ),
]
