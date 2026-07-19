from django_filters import rest_framework as filters

from services.queue_entry.models import QueueEntry


class QueueEntryFilterSet(filters.FilterSet):
    created = filters.DateFromToRangeFilter()
    has_forecast = filters.BooleanFilter(method="filter_has_forecast")

    class Meta:
        model = QueueEntry
        fields = {
            "forecast": ["exact"],
            "deposit": ["exact"],
        }

    def filter_has_forecast(self, queryset, name, value):
        if value:
            return queryset.filter(forecast__isnull=False)
        return queryset.filter(forecast__isnull=True)