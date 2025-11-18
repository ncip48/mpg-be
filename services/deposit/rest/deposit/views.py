from __future__ import annotations

import logging
import os
from decimal import Decimal
from io import BytesIO
from typing import TYPE_CHECKING

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

# Report lab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from core.media import media_to_path
from services.deposit.models import Deposit
from services.deposit.rest.deposit.filtersets import DepositFilterSet
from services.deposit.rest.deposit.serializers import (
    DepositCreateSerializer,
    DepositDetailSerializer,
    DepositListSerializer,
)
from services.order.models.invoice import Invoice

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
    serializer_class = DepositListSerializer
    filterset_class = DepositFilterSet
    search_fields = [
        "order_number",
        "customer__name",
        "invoice__invoice_no",
        "user_name",
    ]
    serializer_map = {
        "create": DepositCreateSerializer,
        "partial_update": DepositCreateSerializer,
        "update": DepositCreateSerializer,
    }

    def create(self, request, *args, **kwargs):
        order_subid = request.data.get("order")

        # 🔹 Validate order before serializer runs
        if order_subid and Deposit.objects.filter(order__subid=order_subid).exists():
            return Response(
                {"detail": f"Order '{order_subid}' already deposited."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DepositCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Use the same detail serializer for response
        response_serializer = DepositDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Handle full update (PUT)
        """
        instance = self.get_object()
        serializer = DepositCreateSerializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        response_serializer = DepositDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle partial update (PATCH)
        """
        instance = self.get_object()
        serializer = DepositCreateSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        response_serializer = DepositDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def generate_invoice_pdf(self, request, subid):
        invoice = get_object_or_404(Invoice, subid=subid)
        order = invoice.order

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=-3.5 * mm,
            bottomMargin=20 * mm,
        )
        elements = []

        # --- STYLES & COLORS ---
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Bold", fontName="Helvetica-Bold", fontSize=10))
        styles.add(ParagraphStyle(name="Small", fontSize=8, parent=styles["Normal"]))
        styles.add(
            ParagraphStyle(name="Right", alignment=TA_RIGHT, parent=styles["Normal"])
        )
        styles.add(
            ParagraphStyle(
                name="RightBold",
                alignment=TA_RIGHT,
                fontName="Helvetica-Bold",
                fontSize=10,
            )
        )
        styles.add(
            ParagraphStyle(
                name="LeftBold",
                alignment=TA_LEFT,
                fontName="Helvetica-Bold",
                fontSize=10,
            )
        )

        TARGET_BLUE = colors.HexColor("#EAD548")

        # --- 1. HEADER (Logo, Bill To, Invoice Info) ---

        # Logo
        logo_path = media_to_path("media/ez_full.png")  # Corrected path
        logo_image = None
        try:
            if os.path.exists(logo_path):
                logo_image = Image(
                    logo_path, width=50 * mm, height=7 * mm, hAlign="LEFT"
                )
            else:
                print(f"⚠️ Logo not found at {logo_path}")
                logo_image = Paragraph("<b>Graphics Family</b>", styles["Bold"])
        except Exception:
            logo_image = Paragraph("<b>Graphics Family</b>", styles["Bold"])

        # Bill To
        bill_to = [
            Spacer(1, 28 * mm),
            logo_image,
            Spacer(1, 5 * mm),
            Paragraph("<b>Invoice To</b>", styles["Bold"]),
            Paragraph(
                f"{order.convection_name}", styles["Normal"]
            ),  # Placeholder from image
            Paragraph(f"{order.customer.address}", styles["Normal"]),  # Placeholder
            Paragraph(f"{order.customer.phone}", styles["Normal"]),  # Placeholder
            # Paragraph(f"M: {order.customer.email}", styles["Normal"]),  # Placeholder
        ]

        # Invoice Info (Right Side)
        invoice_title_table = Table(
            [["INVOICE"]], colWidths=[60 * mm], rowHeights=[40 * mm]
        )
        invoice_title_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), TARGET_BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 35),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 35),
                ]
            )
        )

        invoice_details_data = [
            ["Invoice", f": {invoice.invoice_no}"],
            # ["Account", ": 000 123 456 789"],  # Placeholder from image
            ["Date", f": {invoice.issued_date.strftime('%d %b %Y')}"],
        ]
        invoice_details_table = Table(
            invoice_details_data,
            colWidths=[20 * mm, 40 * mm],
            style=[("FONTNAME", (0, 0), (-1, -1), "Helvetica")],
        )

        invoice_info = [
            invoice_title_table,
            Spacer(1, 5 * mm),
            invoice_details_table,
        ]

        # Combine Header
        header_table = Table(
            [[bill_to, invoice_info]],
            colWidths=[100 * mm, 70 * mm],
            style=[("VALIGN", (0, 0), (-1, -1), "TOP")],
        )
        elements.append(header_table)
        elements.append(Spacer(1, 10 * mm))

        # --- 2. ITEM TABLE ---
        item_data = [
            [
                Paragraph("<b>NO</b>", styles["Bold"]),
                Paragraph("<b>ITEM DESCRIPTION</b>", styles["Bold"]),
                Paragraph("<b>PRICE</b>", styles["RightBold"]),
                Paragraph("<b>QTY</b>", styles["RightBold"]),
                Paragraph("<b>TOTAL</b>", styles["RightBold"]),
            ]
        ]
        total_invoice = Decimal("0.00")
        total_extra_cost = Decimal("0.00")

        # Add Order Items
        for i, item in enumerate(order.items.all(), start=1):
            subtotal = item.subtotal
            total_invoice += subtotal

            product = getattr(item, "product", None)
            product_name = getattr(product, "name", "-")
            variant_type = getattr(item, "variant_type", None)
            variant_code = getattr(variant_type, "code", None)

            display_name = (
                f"{variant_code} - {product_name}" if variant_code else product_name
            )

            # Cell with main description and sub-description
            item_description_cell = [
                Paragraph(display_name, styles["Bold"]),
                Paragraph(item.fabric_type.name, styles["Small"]),
            ]

            item_data.append(
                [
                    str(i),
                    item_description_cell,
                    Paragraph(f"Rp {item.price:,.0f}", styles["Right"]),
                    Paragraph(str(item.quantity), styles["Right"]),
                    Paragraph(f"Rp {subtotal:,.0f}", styles["Right"]),
                ]
            )

        # Add Extra Costs
        for i, cost in enumerate(order.extra_costs.all(), start=len(item_data)):
            total_extra_cost += cost.total_amount

            # Calculate unit price if possible, handle division by zero
            unit_price = Decimal("0.00")
            if cost.quantity:
                unit_price = cost.total_amount / cost.quantity

            item_description_cell = [
                Paragraph(cost.description, styles["Bold"]),
                Paragraph("Biaya Tambahan", styles["Small"]),
            ]

            item_data.append(
                [
                    str(i),
                    item_description_cell,
                    Paragraph(f"Rp {unit_price:,.0f}", styles["Right"]),
                    Paragraph(str(cost.quantity), styles["Right"]),
                    Paragraph(f"Rp {cost.total_amount:,.0f}", styles["Right"]),
                ]
            )

        item_table = Table(
            item_data,
            colWidths=[10 * mm, 80 * mm, 30 * mm, 15 * mm, 30 * mm],
            repeatRows=1,
        )
        item_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), TARGET_BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 1), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                    ("ALIGN", (2, 0), (-1, 0), "RIGHT"),
                ]
            )
        )
        elements.append(item_table)
        elements.append(Spacer(1, 5 * mm))

        # --- 3. TOTALS ---
        sub_total = total_invoice + total_extra_cost
        # vat_rate = Decimal("0.15")  # 15% VAT from image
        # tax = sub_total * vat_rate
        tax = 0
        grand_total = sub_total + tax

        totals_data = [
            # ["SUB TOTAL", f"Rp {sub_total:,.0f}"],
            # ["TAX VAT 15%", f"Rp {tax:,.0f}"],
            [
                Paragraph("<b>GRAND TOTAL</b>", styles["Bold"]),
                Paragraph(f"<b>Rp {grand_total:,.0f}</b>", styles["RightBold"]),
            ],
        ]

        totals_table = Table(totals_data, colWidths=[45 * mm, 30 * mm])
        totals_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    (
                        "LINEABOVE",
                        (0, 2),
                        (1, 2),
                        1,
                        colors.black,
                    ),  # Line above grand total
                    ("TOPPADDING", (0, 2), (1, 2), 5),
                ]
            )
        )
        totals_table.hAlign = "RIGHT"
        elements.append(totals_table)
        elements.append(Spacer(1, 10 * mm))

        # # --- 4. FOOTER (Payment, Terms, Signature) ---
        # payment_info = [
        #     Paragraph("<b>PAYMENT INFO</b>", styles["Bold"]),
        #     Paragraph("Paypal: paypal@company.com", styles["Small"]),
        #     Paragraph("Payonner: info@company.com", styles["Small"]),
        # ]

        # terms = [
        #     Paragraph("<b>TERMS & CONDITIONS</b>", styles["Bold"]),
        #     Paragraph(
        #         "Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod.",
        #         styles["Small"],
        #     ),
        # ]

        # signature = [
        #     # You could place an Image of a signature here
        #     Paragraph("<i>Adi Barbu</i>", styles["Normal"]),
        #     Spacer(1, 3 * mm),
        #     Paragraph("CEO. ADI BARBU", styles["Small"]),
        # ]

        # footer_table = Table(
        #     [[payment_info, terms, signature]], colWidths=[60 * mm, 60 * mm, 50 * mm]
        # )
        # footer_table.setStyle(
        #     [
        #         ("VALIGN", (0, 0), (-1, -1), "TOP"),
        #         ("ALIGN", (2, 0), (2, 0), "LEFT"),  # Align signature
        #     ]
        # )
        # elements.append(footer_table)
        # elements.append(Spacer(1, 15 * mm))  # Space before page bottom

        # --- 5. PAGE BOTTOM (Contact Info) ---
        # This will appear at the end of the content.
        logo_path = media_to_path("media/ez.png")  # Corrected path
        logo_image = None
        try:
            if os.path.exists(logo_path):
                logo_image = Image(
                    logo_path, width=7 * mm, height=7 * mm, hAlign="LEFT"
                )
            else:
                print(f"⚠️ Logo not found at {logo_path}")
                logo_image = Paragraph("<b>Graphics Family</b>", styles["Bold"])
        except Exception:
            logo_image = Paragraph("<b>Graphics Family</b>", styles["Bold"])
        contact_logo = [
            logo_image,
        ]  # Placeholder for logo
        contact_addr = [
            Paragraph(
                "Jl. Kepatihan Industri No. 18/C-05, Gresik - Jawa Timur",
                styles["Small"],
            ),
            # Paragraph("Your Street No. 223 NY USA", styles["Small"]),
        ]
        # contact_phone = [
        #     Paragraph("+00 123 456 789", styles["Small"]),
        #     Paragraph("+00 123 456 789", styles["Small"]),
        # ]
        contact_web = [
            Paragraph("IG: @ezsportswear", styles["Small"]),
            Paragraph("Tiktok: @ezsportswear2", styles["Small"]),
        ]

        contact_table = Table(
            # [[contact_logo, contact_addr, contact_phone, contact_web]],
            [[contact_logo, contact_addr, contact_web]],
            # colWidths=[20 * mm, 65 * mm, 45 * mm, 40 * mm],
            colWidths=[20 * mm, 110 * mm, 40 * mm],
        )

        contact_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    # ALTERNATIVE: This draws all internal lines
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.gray),
                    ("LEFTPADDING", (1, 0), (3, 0), 5 * mm),
                ]
            )
        )
        elements.append(contact_table)

        # --- BUILD ---
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{invoice.invoice_no}.pdf"'
        return response
