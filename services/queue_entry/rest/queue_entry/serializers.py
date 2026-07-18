from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.deposit.rest.deposit.serializers import DepositDetailSerializer, DepositListSerializer
from services.queue_entry.models import QueueEntry

import datetime
import holidays

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
        
        # 🚀 FAST: Build the dictionary directly instead of calling a DRF Serializer
        if instance.created_by:
            data["created_by"] = {
                "pk": instance.created_by.subid,
                # Add any other fields UserSerializerSimple usually returns, e.g.:
                "first_name": instance.created_by.first_name,
                "last_name": instance.created_by.first_name,
                "email": instance.created_by.email,
            }
        else:
            data["created_by"] = None
            
        return data
    
    def get_type(self, obj):
        return "Konveksi" if obj.deposit else "Marketplace"
    
    def get_priority_status(self, obj):
        ps = None
        if obj.order_item and obj.order_item.deposit:
            ps = obj.order_item.deposit.priority_status
        elif obj.order:
            ps = obj.order.priority_status

        return ps.upper() if ps else None

    def get_estimate_sent(self, obj):
        if obj.order_item and obj.order_item.deposit:
            deposit = obj.order_item.deposit
            accepted_at = getattr(deposit, "accepted_at", None)
            lead_time = getattr(deposit, "lead_time", 0)

            if accepted_at and lead_time:
                # Use Indonesian public holidays
                id_holidays = holidays.country_holidays("ID", years=accepted_at.year)

                current_date = accepted_at
                days_added = 0

                while days_added < lead_time:
                    current_date += datetime.timedelta(days=1)

                    # Skip weekends (Saturday=5, Sunday=6)
                    if current_date.weekday() >= 5:
                        continue

                    # Skip Indonesian holidays
                    if current_date in id_holidays:
                        continue

                    days_added += 1

                return current_date.strftime("%Y-%m-%d")
        
        # Fallback to the order's estimated date
        if obj.order:
            return obj.order.estimated_shipping_date
            
        return None