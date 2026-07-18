from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.deposit.rest.deposit.serializers import DepositDetailSerializer, DepositListSerializer
from services.queue_entry.models import QueueEntry

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QueueEntrySerializer",)


class QueueEntrySerializer(BaseModelSerializer):
    """
    Serializer for QueueEntry management.
    """
    type = serializers.SerializerMethodField()
    # sku = serializers.SerializerMethodField()
    priority_status = serializers.SerializerMethodField()
    estimate_sent = serializers.SerializerMethodField()

    class Meta:
        model = QueueEntry
        fields = [
            "pk",
            "type",
            # "sku",
            "priority_status",
            "estimate_sent",
            # "order",
            # "order_item",
            "ticket_number",
            "created_by",
            "details",
            "created",
            "updated",
        ]
        read_only_fields = [
            "pk",
            "ticket_number",
            "created_by",
            "created",
            "updated",
            "type",
        ]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["created_by"] = UserSerializerSimple(instance.created_by).data
        return data
    
    def _get_stock_item(self, obj):
        # Uses the prefetch_related cache. Change 'stock_items' if related_name is different.
        stock_items = obj.stock_items.all()
        return stock_items[0] if stock_items else None
    
    def get_type(self, obj):
        return "Konveksi" if obj.deposit else "Marketplace"
    
    def get_priority_status(self, obj):
        if obj.order_item:
            ps = obj.order_item.deposit.priority_status.upper()
        else:
            ps = obj.order.priority_status.upper()

        return ps

    def get_estimate_sent(self, obj):
        if obj.order_item:
            deposit = DepositListSerializer(obj.order_item.deposit)
            es = deposit.data["estimate_sent"]
        else:
            es = obj.order.estimated_shipping_date

        return es