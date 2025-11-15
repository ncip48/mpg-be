from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderItemViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"order-items", OrderItemViewSet, basename="order-items")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
    path(
        "order-items/<str:subid>/order-form/",
        OrderItemViewSet.as_view(
            {
                "get": "order_form",
                "post": "create_order_form",
                "put": "update_order_form",
                "patch": "partial_update_order_form",
                "delete": "delete_order_form",
            }
        ),
        name="order-form",
    ),
]
