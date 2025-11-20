import django_filters
from django.db.models import Q

from services.order.models.order_item import OrderItem


class OrderItemFilterSet(django_filters.FilterSet):
    order = django_filters.CharFilter(method="filter_order")

    class Meta:
        model = OrderItem
        fields = ["order"]

    def filter_order(self, queryset, name, value):
        """
        Allow searching OrderItem by:
        - order.subid
        - order.identifier
        - order.customer.name
        - order.convection_name
        """
        return queryset.filter(
            Q(order__subid__icontains=value)
            | Q(order__identifier__icontains=value)
            | Q(order__customer__name__icontains=value)
            | Q(order__convection_name__icontains=value)
        )
