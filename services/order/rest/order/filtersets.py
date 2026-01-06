import django_filters

from services.order.models import Order


class OrderFilterSet(django_filters.FilterSet):
    # ForeignKey → filter by subid
    customer = django_filters.CharFilter(
        field_name="customer__subid", lookup_expr="exact"
    )

    created_by = django_filters.CharFilter(
        field_name="created_by__subid", lookup_expr="exact"
    )

    # Choice fields
    order_type = django_filters.CharFilter(field_name="order_type", lookup_expr="exact")

    priority_status = django_filters.CharFilter(
        field_name="priority_status", lookup_expr="exact"
    )

    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    marketplace = django_filters.CharFilter(
        field_name="marketplace", lookup_expr="exact"
    )

    order_choice = django_filters.CharFilter(
        field_name="order_choice", lookup_expr="exact"
    )

    class Meta:
        model = Order
        fields = [
            "customer",
            "order_type",
            "priority_status",
            "status",
            "marketplace",
            "order_choice",
            "created_by",
        ]
