import django_filters

from services.deposit.models import Deposit


class DepositFilterSet(django_filters.FilterSet):
    order = django_filters.CharFilter(field_name="order__subid")
    created_by = django_filters.CharFilter(
        field_name="created_by__subid", lookup_expr="exact"
    )
    is_paid_off = django_filters.BooleanFilter(field_name="is_paid_off")

    is_expired = django_filters.BooleanFilter(method="filter_is_expired")

    class Meta:
        model = Deposit
        fields = ["order", "is_paid_off", "is_expired", "created_by"]

    def filter_is_expired(self, queryset, name, value):
        """
        Expired means:
        - is_expired = True
        - AND is_paid_off = False
        """
        if value is True:
            return queryset.filter(
                is_expired=True,
                is_paid_off=False,
            )

        if value is False:
            return queryset.exclude(is_expired=False)

        return queryset
