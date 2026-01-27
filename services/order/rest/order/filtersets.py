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
    is_deposit = django_filters.BooleanFilter(method="filter_is_deposit")

    class Meta:
        model = Order
        fields = [
            "is_deposit",
            "customer",
            "order_type",
            "priority_status",
            "status",
            "marketplace",
            "order_choice",
            "created_by",
        ]

    def filter_is_deposit(self, queryset, name, value):
        if value:
            return queryset.filter(deposits__isnull=False)
        return queryset.filter(deposits__isnull=True)
