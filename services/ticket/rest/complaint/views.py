from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.ticket.models.complaint_action import ComplaintAction
from services.ticket.models.complaint_ticket import ComplaintTicket
from services.ticket.rest.complaint.filtersets import ComplaintTicketFilterSet
from services.ticket.rest.complaint.serializers import (
    ComplaintActionSerializer,
    ComplaintTicketSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ComplaintTicketViewSet",
    "ComplaintActionViewSet",
)


class ComplaintTicketViewSet(BaseViewSet):
    """
    ViewSet for Customer Complaint Tickets.
    """

    queryset = ComplaintTicket.objects.all()
    serializer_class = ComplaintTicketSerializer
    lookup_field = "subid"

    search_fields = [
        "subid",
        "customer_name",
        "customer_id",
        "order__subid",
    ]

    required_perms = [
        "ticket.add_complaintticket",
        "ticket.change_complaintticket",
        "ticket.delete_complaintticket",
        "ticket.view_complaintticket",
    ]

    my_tags = ["Complaint Tickets"]

    filterset_class = ComplaintTicketFilterSet

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = serializer.save(created_by=request.user)

        return Response(
            self.get_serializer(ticket).data,
            status=status.HTTP_201_CREATED,
        )


class ComplaintActionViewSet(BaseViewSet):
    """
    ViewSet for QC Verification & Approval Actions.
    """

    queryset = ComplaintAction.objects.select_related("ticket")
    serializer_class = ComplaintActionSerializer

    search_fields = [
        "ticket__subid",
        "action_type",
        "result",
    ]

    required_perms = [
        "ticket.add_complaintaction",
        "ticket.change_complaintaction",
        "ticket.delete_complaintaction",
        "ticket.view_complaintaction",
    ]

    my_tags = ["Complaint Actions"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.save(acted_by=request.user)

        # Optional: auto update ticket status
        ticket = action.ticket
        if action.action_type == "QC_VERIFY":
            ticket.status = (
                "QC_ACCEPTED" if action.result == "ACCEPTED" else "QC_REJECTED"
            )
        elif action.action_type == "APPROVAL":
            ticket.status = "APPROVED"

        ticket.save(update_fields=["status"])

        return Response(
            self.get_serializer(action).data,
            status=status.HTTP_201_CREATED,
        )
