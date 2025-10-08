from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.customer.models.customer import Customer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "CustomerSerializer",
    "CustomerSerializerSimple",
)

class CustomerSerializer(BaseModelSerializer):
    """
    Serializer for Customer management by superusers.
    Handles CRUD for Customer and assignment of permissions.
    """

    class Meta:
        model = Customer
        fields = ['pk', 'identity', 'name', 'phone', 'address', 'source']
        extra_kwargs = {
            'identity': {'read_only': True},
        }

class CustomerSerializerSimple(BaseModelSerializer):
    """
    Serializer for Customer management by superusers.
    Handles CRUD for Customer and assignment of permissions.
    """

    class Meta:
        model = Customer
        fields = ['pk', 'name']