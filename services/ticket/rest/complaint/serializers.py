from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.customer.models.customer import Customer
from services.order.models.order import Order
from services.ticket.models.complaint_action import ComplaintAction
from services.ticket.models.complaint_ticket import ComplaintTicket

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ComplaintTicketSerializer",
    "ComplaintActionSerializer",
)


class ComplaintActionSerializer(BaseModelSerializer):
    """
    Serializer for QC Verification & Approval Action.
    """

    ticket = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=ComplaintTicket.objects.all(),
        required=True,
    )

    class Meta:
        model = ComplaintAction
        fields = [
            "pk",
            "ticket",
            "action_type",
            "result",
            "note",
            "estimated_finish_date",
            "acted_by",
            "created",
        ]
        read_only_fields = ["acted_by"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["acted_by"] = UserSerializerSimple(instance.acted_by).data
        return data


class ComplaintTicketSerializer(BaseModelSerializer):
    """
    Serializer for Complaint Ticket (Customer Complaint & Return).
    """

    order = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Order.objects.all(),
        required=True,
    )
    last_action = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintTicket
        fields = [
            "pk",
            "order",
            "customer_name",
            "received_date",
            "complaint_type",
            "customer_request",
            "status",
            "evidence_image",
            "last_action",
            "created",
            "updated",
        ]

    def get_last_action(self, obj):
        """
        Return latest ComplaintAction (if any)
        """
        action = obj.actions.order_by("-created").first()
        if not action:
            return None
        return ComplaintActionSerializer(action).data
