from services.deposit.models import Deposit
import django_filters


class DepositFilterSet(django_filters.FilterSet):
    # ForeignKey filters (by PK)
    order = django_filters.CharFilter(field_name="order__subid")
    is_paid_off = django_filters.BooleanFilter(field_name="is_paid_off")
    is_expired = django_filters.BooleanFilter(field_name="is_expired")

    class Meta:
        model = Deposit
        fields = ["order", "is_paid_off", "is_expired"]
