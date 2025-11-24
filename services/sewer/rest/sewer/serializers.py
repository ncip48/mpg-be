from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.serializers import BaseModelSerializer
from services.sewer.models import Sewer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("SewerSerializer",)


class SewerSerializer(BaseModelSerializer):
    """
    Serializer for Sewer management by superusers.
    Handles CRUD for Sewer and assignment of permissions.
    """

    class Meta:
        model = Sewer
        fields = ["pk", "name"]
