from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.warehouse.models import Receiving
from services.warehouse.models.purchase_order import PurchaseOrder
from services.warehouse.rest.purchase_order.serializers import PurchaseOrderSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ReceivingSerializer",)


class ReceivingSerializer(BaseModelSerializer):
    """
    Serializer for Warehouse Receiving (Penerimaan).
    """

    purchase_order = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=PurchaseOrder.objects.all(),
        required=True,
    )

    class Meta:
        model = Receiving
        fields = [
            "pk",
            "purchase_order",
            "invoice_number",
            "qty_received",
            "date_received",
            "received_by",
        ]
        read_only_fields = ["received_by"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["purchase_order"] = PurchaseOrderSerializer(instance.material).data
        data["received_by"] = UserSerializerSimple(instance.received_by).data
        return data
