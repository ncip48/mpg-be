import django_filters

from services.forecast.models import Forecast


class ForecastFilterSet(django_filters.FilterSet):
    is_print = django_filters.BooleanFilter(field_name="print_status")

    class Meta:
        model = Forecast
        fields = ["print_status"]
