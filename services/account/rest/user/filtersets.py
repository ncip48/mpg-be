import django_filters

from services.deposit.models import Deposit


class UserFilterSet(django_filters.FilterSet):
    # ForeignKey filters (by PK)
    role = django_filters.CharFilter(field_name="role__subid")

    class Meta:
        model = Deposit
        fields = ["role"]
