from __future__ import annotations
from decimal import Decimal
from io import BytesIO
import os
from typing import TYPE_CHECKING
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from core.common.viewsets import BaseViewSet
from services.deposit.rest.deposit.filtersets import DepositFilterSet
from services.order.models.invoice import Invoice
from services.deposit.rest.deposit.serializers import (
    OrderCreateSerializer,
    OrderKonveksiListSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderMarketplaceListSerializer,
)
from services.deposit.models import Deposit

# Report lab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from django.http import HttpResponse

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("DepositViewSet",)


class DepositViewSet(BaseViewSet):
    required_perms = [
        "order.can_add_deposit",
        "order.can_change_deposit",
        "order.can_delete_deposit",
        "order.can_view_deposit",
    ]
    my_tags = ["Deposits"]
    queryset = (
        Deposit.objects.select_related("order", "invoice")
        .prefetch_related("items")
        .order_by("-created")
    )
    lookup_field = "subid"
    serializer_class = OrderListSerializer
    # filterset_fields = [
    #     "is_paid_off",
    #     "is_expired",
    # ]
    filterset_class = DepositFilterSet
    search_fields = [
        "order_number",
        "customer__name",
        "invoice__invoice_no",
        "user_name",
    ]
    serializer_map = {
        "create": OrderCreateSerializer,
        "konveksi": OrderKonveksiListSerializer,
        "marketplace": OrderMarketplaceListSerializer,
        "partial_update": OrderCreateSerializer,
        "update": OrderCreateSerializer,
    }

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the current action.
        Defaults to `serializer_class` if no match in `serializer_map`.
        """
        # Handle "list" with query param same as before
        if (
            self.action == "list"
            and self.request.query_params.get("order_type") == "konveksi"
        ):
            serializer = self.serializer_map.get("konveksi", None)
            if serializer is not None:
                return serializer

        if (
            self.action == "list"
            and self.request.query_params.get("order_type") == "marketplace"
        ):
            serializer = self.serializer_map.get("marketplace", None)
            if serializer is not None:
                return serializer

        if self.action == "retrieve":
            obj = self.get_object()
            if hasattr(obj, "order_type"):
                if obj.order_type == "konveksi":
                    serializer = self.serializer_map.get("konveksi", None)
                    if serializer is not None:
                        return serializer
                elif obj.order_type == "marketplace":
                    serializer = self.serializer_map.get("marketplace", None)
                    if serializer is not None:
                        return serializer

        return self.serializer_map.get(self.action, self.serializer_class)

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Use the same detail serializer for response
        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Handle full update (PUT)
        """
        instance = self.get_object()
        serializer = OrderCreateSerializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle partial update (PATCH)
        """
        instance = self.get_object()
        serializer = OrderCreateSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def generate_invoice_pdf(self, request, subid):
        invoice = get_object_or_404(Invoice, order__subid=subid)
        order = invoice.order

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm
        )
        elements = []
        styles = getSampleStyleSheet()

        # --- HEADER ---
        logo_path = os.path.join(settings.MEDIA_ROOT, "/logo.webp")
        try:
            if os.path.exists(logo_path):
                elements.append(Image(logo_path, width=120, height=60))
            else:
                print(f"⚠️ Logo not found at {logo_path}")
        except Exception:
            elements.append(Paragraph("<b>EZ Sportswear</b>", styles["Title"]))
        elements.append(Spacer(1, 5))

        elements.append(
            Paragraph(
                "Ruko Palma Grandia RG2/17-19<br/>Kota Surabaya, Indonesia",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 10))

        # --- CUSTOMER + INVOICE INFO ---
        info_data = [
            ["<b>NAMA KONVEKSI</b>", f": {order.customer.name}"],
            ["<b>Nomor Invoice</b>", f": {invoice.invoice_no}"],
            ["<b>Tanggal Invoice</b>", f": {invoice.issued_date.strftime('%d %B %Y')}"],
            ["<b>Tanggal Kirim</b>", f": {invoice.delivery_date.strftime('%d %B %Y')}"],
        ]
        info_table = Table(info_data, colWidths=[100 * mm, 70 * mm])
        elements.append(info_table)
        elements.append(Spacer(1, 10))

        # --- ITEM TABLE ---
        elements.append(Paragraph("<b>INVOICE</b>", styles["Heading3"]))

        item_data = [["No.", "Nama Item", "Jenis Kain", "Harga Satuan", "Qty", "TOTAL"]]
        total_invoice = Decimal("0.00")

        for i, item in enumerate(order.items.all(), start=1):
            subtotal = item.subtotal
            total_invoice += subtotal

            # Get basic fields safely
            product = getattr(item, "product", None)
            product_name = getattr(product, "name", "-")

            variant_type = getattr(item, "variant_type", None)
            variant_code = getattr(variant_type, "code", None)

            # Combine product name with variant code (e.g., "VAR01 - Kaos Polos Premium")
            if variant_code:
                display_name = f"{variant_code} - {product_name}"
            else:
                display_name = product_name

            item_data.append(
                [
                    str(i),
                    display_name,
                    item.fabric_type.name,
                    f"Rp {item.price:,.0f}",
                    str(item.quantity),
                    f"Rp {subtotal:,.0f}",
                ]
            )

        for _ in range(len(item_data), 12):  # fill empty rows to look consistent
            item_data.append(["", "", "", "", "", ""])

        t = Table(
            item_data, colWidths=[15 * mm, 60 * mm, 35 * mm, 30 * mm, 20 * mm, 30 * mm]
        )
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6EEF8")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        elements.append(t)

        elements.append(Spacer(1, 5))
        elements.append(
            Paragraph(
                f"<b>TOTAL INVOICE :</b> Rp {total_invoice:,.0f}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 10))

        # --- EXTRA COSTS ---
        elements.append(Paragraph("<b>BIAYA LAIN</b>", styles["Heading3"]))

        extra_data = [["No.", "Keterangan", "Qty", "Total Harga"]]
        total_extra_cost = Decimal("0.00")

        for i, cost in enumerate(order.extra_costs.all(), start=1):
            total_extra_cost += cost.total_amount
            color = colors.red if cost.total_amount < 0 else colors.black
            extra_data.append(
                [
                    str(i),
                    cost.description,
                    str(cost.quantity),
                    f"Rp {cost.total_amount:,.0f}",
                ]
            )

        t2 = Table(extra_data, colWidths=[15 * mm, 100 * mm, 20 * mm, 30 * mm])
        t2.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6EEF8")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        elements.append(t2)

        grand_total = total_invoice + total_extra_cost
        elements.append(Spacer(1, 5))
        elements.append(
            Paragraph(
                f"<b>TOTAL BIAYA LAIN :</b> Rp {total_extra_cost:,.0f}",
                styles["Normal"],
            )
        )
        elements.append(
            Paragraph(
                f"<b>SUB TOTAL PEMBELIAN :</b> Rp {grand_total:,.0f}",
                styles["Heading3"],
            )
        )
        elements.append(Spacer(1, 10))

        # --- FOOTER NOTE ---
        note_data = [
            [
                Paragraph(
                    "<b>KETERANGAN :</b><br/>"
                    "Pembayaran transfer ke rekening <b>BCA 5105250123</b> a.n. <b>PT. Mardi Persada Group</b><br/><br/>"
                    "Jika pembayaran DP tidak dilakukan segera, maka resiko antrian design penuh "
                    "(yang menyebabkan proses pengerjaan mundur) akan ditanggung pembeli.",
                    styles["Normal"],
                )
            ]
        ]
        note_table = Table(note_data, colWidths=[180 * mm])
        note_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.yellow),
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elements.append(note_table)

        # --- BUILD ---
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{invoice.invoice_no}.pdf"'
        return response
