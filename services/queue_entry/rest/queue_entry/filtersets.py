from django_filters import rest_framework as filters

from services.queue_entry.models import QueueEntry


class QueueEntryFilterSet(filters.FilterSet):
    created = filters.DateFromToRangeFilter()

    class Meta:
        model = QueueEntry
        fields = {
            "forecast": ["exact"],
            "deposit": ["exact"],
        }