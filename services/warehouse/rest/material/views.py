from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models import F
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.warehouse.models import Issuing, Material, Receiving, StockOpname
from services.warehouse.rest.material.serializers import MaterialSerializer

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
    filterset_fields = ["category"]
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
        """
        Custom Dashboard: Aggregates In/Out/Opname history for one material.
        """
        material = self.get_object()

        # Fetch Transactions
        receivings = (
            Receiving.objects.filter(purchase_order__material=material)
            .annotate(source_desc=F("purchase_order__supplier__name"))
            .values("date_received", "qty_received", "source_desc", "invoice_number")
        )

        issuings = (
            Issuing.objects.filter(material=material)
            .annotate(forecast_desc=F("forecast_date"))
            .values("date_out", "qty_out", "forecast_desc")
        )

        opnames = StockOpname.objects.filter(material=material).values(
            "date_so", "qty_actual", "qty_system"
        )

        history = []

        # Map Receiving (IN)
        for r in receivings:
            history.append(
                {
                    "date": r["date_received"],
                    "activity": _("Masuk (In)"),
                    "description": f"From {r['source_desc']} (Inv: {r['invoice_number']})",
                    "qty_in": r["qty_received"],
                    "qty_out": 0,
                }
            )

        # Map Issuing (OUT)
        for i in issuings:
            history.append(
                {
                    "date": i["date_out"],
                    "activity": _("Keluar (Out)"),
                    "description": f"Forecast: {i['forecast_desc']}",
                    "qty_in": 0,
                    "qty_out": i["qty_out"],
                }
            )

        # Map Opname (ADJUST)
        for o in opnames:
            history.append(
                {
                    "date": o["date_so"],
                    "activity": _("Stock Opname"),
                    "description": f"System: {o['qty_system']} -> Actual: {o['qty_actual']}",
                    "qty_in": 0,
                    "qty_out": 0,
                }
            )

        # Sort by date descending
        history.sort(key=lambda x: x["date"], reverse=True)

        return Response(
            {
                "material": material.name,
                "current_stock": material.current_stock,
                "unit": material.unit,
                "history": history,
            }
        )
