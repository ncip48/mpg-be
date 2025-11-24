from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.sewer.models import Sewer
from services.sewer.rest.sewer.serializers import SewerSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("SewerViewSet",)


class SewerViewSet(BaseViewSet):
    """
    A viewset for viewing and editing sewers.
    Accessible only by superusers.
    """

    queryset = Sewer.objects.all()
    serializer_class = SewerSerializer
    lookup_field = "subid"
    search_fields = [
        "name",
    ]
    required_perms = [
        "sewer.add_sewer",
        "sewer.change_sewer",
        "sewer.delete_sewer",
        "sewer.view_sewer",
    ]
    my_tags = ["Sewers"]
    serializer_map = {
        "autocomplete": SewerSerializer,
    }
