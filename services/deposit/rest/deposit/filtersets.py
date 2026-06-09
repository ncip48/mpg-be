import django_filters

from services.deposit.models import Deposit


class DepositFilterSet(django_filters.FilterSet):
    order = django_filters.CharFilter(field_name="order__subid")
    created_by = django_filters.CharFilter(
        field_name="created_by__subid", lookup_expr="exact"
    )
    is_paid_off = django_filters.BooleanFilter(field_name="is_paid_off")

    is_expired = django_filters.BooleanFilter(method="filter_is_expired")
    
    is_acc_form = django_filters.BooleanFilter(method="filter_is_acc_form")
    
    paid_off_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Deposit
        fields = ["order", "is_paid_off", "is_expired", "created_by", "paid_off_at"]

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
            return queryset.exclude(is_expired=True, is_paid_off=False)

        return queryset
    
    def filter_is_acc_form(self, queryset, name, value):
        print("value =", value, type(value))

        if value is True:
            return queryset.filter(accepted_at__isnull=False)

        if value is False:
            return queryset.filter(accepted_at__isnull=True)

        return queryset
