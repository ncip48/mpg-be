from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import django_filters

from services.defect.models import Reject

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("RejectFilterSet",)


class RejectFilterSet(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter()
    qty = django_filters.RangeFilter()
    hpp = django_filters.RangeFilter()

    class Meta:
        model = Reject
        fields = {
            "content_type": ["exact"],
            "object_id": ["exact"],
            "defect": ["exact", "icontains"],
            "qty": ["exact", "gte", "lte"],
            "hpp": ["exact", "gte", "lte"],
            "created": ["exact", "gte", "lte"],
        }