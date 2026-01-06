import django_filters

from services.forecast.models import Forecast


class SewerDistributionFilterSet(django_filters.FilterSet):
    # ForeignKey → filter by subid
    forecast = django_filters.CharFilter(field_name="subid", lookup_expr="exact")

    distributed_by = django_filters.CharFilter(
        field_name="sewer_distributions__distributed_by__subid", lookup_expr="exact"
    )

    sewer = django_filters.CharFilter(
        field_name="sewer_distributions__sewer__subid", lookup_expr="exact"
    )

    # Boolean
    is_full = django_filters.BooleanFilter(field_name="sewer_distributions__is_full")

    class Meta:
        model = Forecast
        fields = [
            "forecast",
            "distributed_by",
            "sewer",
            "is_full",
        ]
