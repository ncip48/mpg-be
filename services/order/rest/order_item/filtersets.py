import django_filters

from services.order.models.order_item import OrderItem


class OrderItemFilterSet(django_filters.FilterSet):
    # ForeignKey filters (by PK)
    order = django_filters.CharFilter(field_name="order__subid")

    class Meta:
        model = OrderItem
        fields = [
            "order",
        ]
