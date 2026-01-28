import django_filters
from django.db.models import Q


class PrinterFabricBaseFilterSet(django_filters.FilterSet):
    printer = django_filters.CharFilter(method="filter_printer")
    fabric_type = django_filters.CharFilter(method="filter_fabric_type")

    def filter_printer(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(
                is_stock=True,
                stock_items__product__printer__subid=value,
            )
            | Q(
                is_stock=False,
                order_item__isnull=False,
                order_item__product__printer__subid=value,
            )
            | Q(
                is_stock=False,
                order_item__isnull=True,
                order__order_forms__printer__subid=value,
            )
        ).distinct()

    def filter_fabric_type(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(
                is_stock=True,
                stock_items__fabric_type__subid=value,
            )
            | Q(
                is_stock=False,
                order_item__isnull=False,
                order_item__fabric_type__subid=value,
            )
            | Q(
                is_stock=False,
                order_item__isnull=True,
                order__order_forms__fabric_type__subid=value,
            )
        ).distinct()
