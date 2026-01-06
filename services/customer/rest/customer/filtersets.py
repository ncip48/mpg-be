import django_filters

from services.customer.models import Customer


class CustomerFilterSet(django_filters.FilterSet):
    # Choice field
    source = django_filters.CharFilter(field_name="source", lookup_expr="exact")

    class Meta:
        model = Customer
        fields = ["source"]
