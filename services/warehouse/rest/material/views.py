from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models import F
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.warehouse.models import Material
from services.warehouse.rest.material.serializers import MaterialSerializer
from django.utils.dateparse import parse_date
from services.warehouse.rest.material.services.stock_card import MaterialStockCardService

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)

__all__ = ("MaterialViewSet",)


class MaterialViewSet(BaseViewSet):
    """
    A viewset for managing Raw Materials.
    Includes 'stock_card' dashboard action.
    """

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    lookup_field = "subid"
    search_fields = ["name", "code", "category"]
    filterset_fields = ["category", "unit"]
    ordering_fields = ["pk"]
    ordering = ["-pk"]
    required_perms = [
        "warehouse.add_material",
        "warehouse.change_material",
        "warehouse.delete_material",
        "warehouse.view_material",
    ]
    my_tags = ["Materials"]
    serializer_map = {
        "autocomplete": MaterialSerializer,
    }

    @action(detail=True, methods=["get"], url_path="stock-card")
    def stock_card(self, request: Request, subid: str | None = None) -> Response:
        material = self.get_object()

        start_date = parse_date(request.query_params.get("start_date"))
        end_date = parse_date(request.query_params.get("end_date"))

        service = MaterialStockCardService(
            material=material,
            start_date=start_date,
            end_date=end_date,
        )

        history = service.get_history()

        return Response(
            {
                "material": material.name,
                "current_stock": material.current_stock,
                "unit": material.unit,
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                },
                "history": list(history),  # force evaluation
            }
        )
