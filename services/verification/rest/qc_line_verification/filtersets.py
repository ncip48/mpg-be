from services.forecast.rest.forecast.filtersets import ForecastFilterSet
import django_filters

from services.forecast.models import Forecast


class QCLineVerificationFilterSet(ForecastFilterSet):
    is_approved = django_filters.BooleanFilter(
        field_name="qc_line_verifications__is_approved"
    )
    type = django_filters.CharFilter(
        method="filter_type",
        label="Type",
    )

    class Meta:
        model = Forecast
        fields = ["is_approved", "type"]

    def filter_type(self, queryset, name, value):
        if value == "stock":
            return queryset.filter(is_stock=True)
        if value == "konveksi":
            return queryset.filter(order__order_type="konveksi")
        if value == "marketplace":
            return queryset.filter(order__order_type="marketplace")

        return queryset
