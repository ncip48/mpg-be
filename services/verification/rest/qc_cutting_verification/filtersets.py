from services.forecast.rest.forecast.filtersets import ForecastFilterSet
import django_filters

from services.forecast.models import Forecast


class QCCuttingVerificationFilterSet(ForecastFilterSet):
    is_approved = django_filters.BooleanFilter(
        field_name="qc_cutting_verifications__is_approved"
    )
    type = django_filters.CharFilter(
        method="filter_type",
        label="Type",
    )
    has_sewer = django_filters.BooleanFilter(
        method="filter_has_sewer",
        label="Has Sewer",
    )

    class Meta:
        model = Forecast
        fields = ["is_approved", "type", "has_sewer"]

    def filter_type(self, queryset, name, value):
        if value == "stock":
            return queryset.filter(is_stock=True)
        if value == "konveksi":
            return queryset.filter(order__order_type="konveksi")
        if value == "marketplace":
            return queryset.filter(order__order_type="marketplace")

        return queryset

    def filter_has_sewer(self, queryset, name, value):
        if value:
            return queryset.filter(sewer_distributions__isnull=False)
        if not value:
            return queryset.filter(sewer_distributions__isnull=True)
        return queryset
