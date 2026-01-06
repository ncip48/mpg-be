import django_filters

from services.account.models import User


class UserFilterSet(django_filters.FilterSet):
    roles = django_filters.CharFilter(method="filter_roles")

    def filter_roles(self, queryset, name, value):
        role_ids = value.split(",")
        return queryset.filter(roles__subid__in=role_ids).distinct()

    class Meta:
        model = User
        fields = ["roles"]
