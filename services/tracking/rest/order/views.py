from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from services.tracking.rest.order.serializers import TrackingSerializer

logger = logging.getLogger(__name__)

__all__ = ("TrackingAPIView",)


class TrackingAPIView(APIView):
    """
    GET /api/tracking/?identifier=ORD000001
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = TrackingSerializer(
            data={
                "identifier": request.query_params.get("identifier"),
            }
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )