import django_filters

from services.forecast.models.forecast import Forecast


class QCFinishingFilterSet(django_filters.FilterSet):
    has_qc_finishing = django_filters.BooleanFilter(
        method="filter_has_qc_finishing",
        label="Has QC Finishing",
    )

    class Meta:
        model = Forecast
        fields = [
            # keep your existing filters here
            "has_qc_finishing",
        ]

    def filter_has_qc_finishing(self, queryset, name, value):
        """
        value = True  -> Forecast WITH QCFinishing
        value = False -> Forecast WITHOUT QCFinishing
        """
        if value is True:
            return queryset.filter(qc_finishings__isnull=False)
        if value is False:
            return queryset.filter(qc_finishings__isnull=True)

        return queryset
