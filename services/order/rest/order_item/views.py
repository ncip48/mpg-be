from __future__ import annotations

import io
import logging
import os
from typing import TYPE_CHECKING

from django.http import FileResponse, HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# --- ReportLab Imports ---
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from core.media import media_to_path
from services.order.models.order_item import OrderItem
from services.order.rest.order_form.serializers import OrderFormSerializer
from services.order.rest.order_item.filtersets import OrderItemFilterSet
from services.order.rest.order_item.serializers import OrderItemSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderItemViewSet",)


class OrderItemViewSet(BaseViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = "subid"
    ordering_fields = ["pk"]
    ordering = ["-pk"]
    filterset_class = OrderItemFilterSet

    search_fields = ["product__name", "deposit__order__customer__name"]

    required_perms = [
        "order.add_orderform",
        "order.change_orderform",
        "order.delete_orderform",
        "order.view_orderform",
    ]

    my_tags = ["Order Forms"]

    serializer_map = {
        # Allow using same serializer for create/update
        "create": OrderFormSerializer,
        "partial_update": OrderFormSerializer,
        "update": OrderFormSerializer,
    }

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def order_form(self, request, *args, **kwargs):
        order_item = self.get_object()  # get OrderItem by subid from URL

        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderFormSerializer(order_form)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_order_form(self, request, *args, **kwargs):
        order_item = self.get_object()  # lookup OrderItem by subid

        # Check if an OrderForm already exists for this OrderItem
        if order_item.order_forms.exists():
            return Response(
                {"detail": "Order form already exists for this order item."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare incoming data
        data = request.data.copy()
        data["order_item"] = order_item.subid  # SlugRelatedField expects subid

        serializer = OrderFormSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_order_form(self, request, *args, **kwargs):
        """Full update (PUT) for the order form attached to this OrderItem."""
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data["order_item"] = order_item.subid  # prevent changing FK

        serializer = OrderFormSerializer(
            order_form,
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update_order_form(self, request, *args, **kwargs):
        """Partial update (PATCH) for the order form."""
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data["order_item"] = order_item.subid  # ensure FK cannot be modified

        serializer = OrderFormSerializer(
            order_form,
            data=data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_order_form(self, request, *args, **kwargs):
        """Delete the order form for this OrderItem."""
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        order_form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def generate_pdf(self, request, *args, **kwargs):
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response({"detail": "Order form not found"}, status=404)

        # Serialize JSON data
        serializer = OrderFormSerializer(order_form)
        data = serializer.data

        # --- Create PDF in memory ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm,
            # rightMargin=1.5 * cm,
            # leftMargin=1.5 * cm,
            # topMargin=1.5 * cm,
            # bottomMargin=1.5 * cm,
        )

        story = []
        styles = getSampleStyleSheet()

        # --- Define Custom Styles based on the screenshot ---

        # Style for section titles (e.g., "PRINTER & BAHAN")
        styles.add(
            ParagraphStyle(
                name="SectionTitle",
                fontName="Helvetica-Bold",
                fontSize=9,
                textColor=colors.white,
                backColor=colors.black,
                alignment=TA_CENTER,
                # spaceAfter=4,
                spaceAfter=0,
                leftIndent=-0.5,
                rightIndent=1.5,
                padding=(4, 4, 4, 4),
            )
        )

        # Style for the body text inside tables
        styles.add(
            ParagraphStyle(
                name="Body",
                fontName="Helvetica",
                fontSize=8,
                alignment=TA_LEFT,
            )
        )

        # Style for placeholder text (for images)
        styles.add(
            ParagraphStyle(
                name="Placeholder",
                fontName="Helvetica-Oblique",
                fontSize=8,
                textColor=colors.darkgrey,
                alignment=TA_CENTER,
            )
        )

        # Style for logo cell titles
        styles.add(
            ParagraphStyle(
                name="LogoTitle",
                fontName="Helvetica-Bold",
                fontSize=7,
                alignment=TA_CENTER,
                spaceAfter=4,
            )
        )

        # Page 2 - Header Row Styles
        styles.add(
            ParagraphStyle(
                name="H_DarkBlue",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.black,
                backColor=colors.HexColor("#90D5FF"),
                alignment=TA_CENTER,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H_Black",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.white,
                backColor=colors.black,
                alignment=TA_CENTER,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H_Yellow",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.black,
                backColor=colors.yellow,
                alignment=TA_CENTER,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H_Green",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.white,
                backColor=colors.green,
                alignment=TA_CENTER,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H_Blue",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.white,
                backColor=colors.blue,
                alignment=TA_CENTER,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H_Orange",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.black,
                backColor=colors.orange,
                alignment=TA_CENTER,
                padding=2,
            )
        )

        # Page 2 - Group Header Styles
        styles.add(
            ParagraphStyle(
                name="HeaderGender",
                fontName="Helvetica-Bold",
                fontSize=9,
                textColor=colors.black,
                backColor=colors.HexColor("#90EE90"),  # Light Green
                alignment=TA_CENTER,
                leftIndent=4,
                padding=3,
            )
        )
        styles.add(
            ParagraphStyle(
                name="HeaderSize",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.black,
                alignment=TA_CENTER,
                leftIndent=4,
                padding=3,
            )
        )

        # Page 2 - Body Cell Styles
        styles.add(
            ParagraphStyle(
                name="BodyCellCenter",
                fontName="Helvetica",
                fontSize=8,
                alignment=TA_CENTER,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodyCellLeft",
                fontName="Helvetica",
                fontSize=8,
                alignment=TA_LEFT,
                leftIndent=4,
                padding=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="TotalCell",
                fontName="Helvetica-Bold",
                fontSize=9,
                alignment=TA_CENTER,
                padding=2,
            )
        )

        # We will build the layout in two main columns
        left_story = []
        right_story = []

        # === LEFT COLUMN ===

        # --- 1. PRINTER & BAHAN ---
        left_story.append(Paragraph("PRINTER & BAHAN", styles["SectionTitle"]))
        p_data = [
            [
                Paragraph("<b>BAHAN</b>", styles["Body"]),
                Paragraph(data["order_item_display"]["fabric_type"], styles["Body"]),
            ],
            [
                Paragraph("<b>PRINTER</b>", styles["Body"]),
                Paragraph(data["printer"]["name"], styles["Body"]),
            ],
        ]
        p_table = Table(p_data, colWidths=[4 * cm, 5.5 * cm])
        p_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        left_story.append(p_table)
        # left_story.append(Spacer(1, 0.5 * cm))

        # --- 2. IDENTITAS ---
        left_story.append(Paragraph("IDENTITAS", styles["SectionTitle"]))
        i_data = [
            [
                Paragraph(
                    f"<b>{data['deposit']['priority_status'].upper()}</b>",
                    styles["Body"],
                ),
                Paragraph(data["customer"]["name"], styles["Body"]),
            ],
            [
                Paragraph("<b>ID NUMBER</b>", styles["Body"]),
                Paragraph(data["deposit"]["order"]["identifier"], styles["Body"]),
            ],
            [
                Paragraph("<b>NAMA TIM</b>", styles["Body"]),
                Paragraph(data["team_name"], styles["Body"]),
            ],
        ]
        i_table = Table(i_data, colWidths=[4 * cm, 5.5 * cm])
        i_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, 0),
                        colors.red
                        if data["deposit"]["priority_status"].upper() == "URGENT"
                        else colors.yellow,
                    ),  # "URGENT" row
                    ("BACKGROUND", (0, 2), (0, 2), colors.orange),  # "NAMA TIM" row
                ]
            )
        )
        left_story.append(i_table)
        # left_story.append(Spacer(1, 0.5 * cm))

        def create_design_image(json_key):
            val = data.get(json_key)

            # Convert media URL to real filesystem path
            real_path = media_to_path(val)

            elements = []

            if real_path and os.path.exists(real_path):
                try:
                    img = Image(real_path, width=2.7 * cm, height=2.7 * cm)
                    elements.append(img)
                except Exception as e:
                    elements.append(
                        Paragraph(
                            f"<i>(Failed to load image: {e})</i>", styles["Placeholder"]
                        )
                    )
            else:
                placeholder_val = val if val else "N/A"
                elements.append(
                    Paragraph(f"<i>({placeholder_val})</i>", styles["Placeholder"])
                )

            elements.append(Spacer(1, 0.1 * cm))
            return elements

        # --- 3. DESAIN PRODUK ---
        left_story.append(Paragraph("DESAIN PRODUK", styles["SectionTitle"]))
        # Placeholder cells for images
        front_cell = [
            Paragraph("<b>DEPAN</b>", styles["LogoTitle"]),
            Spacer(1, 2 * cm),
            create_design_image("design_front"),
            Spacer(1, 2 * cm),
        ]
        back_cell = [
            Paragraph("<b>BELAKANG</b>", styles["LogoTitle"]),
            Spacer(1, 2 * cm),
            create_design_image("design_back"),
            Spacer(1, 2 * cm),
        ]
        d_table = Table([[front_cell, back_cell]], colWidths=[4.75 * cm, 4.75 * cm])
        d_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        left_story.append(d_table)
        # left_story.append(Spacer(1, 0.5 * cm))

        # --- 4. SPESIFIKASI TEKNIS ---
        left_story.append(Paragraph("SPESIFIKASI TEKNIS", styles["SectionTitle"]))
        s_data = [
            [
                Paragraph(f"<b>{key}</b>", styles["Body"]),
                Paragraph(str(val), styles["Body"]),
            ]
            for key, val in [
                (
                    "JUMLAH TOTAL",
                    f"{data['total_qty']} {data['order_item_display']['unit']}",
                ),
                ("POLA JERSEY", data["jersey_pattern"]),
                ("JENIS JERSEY", data["jersey_type"]),
                ("CUTTING JERSEY", data["jersey_cutting"]),
                ("KERAH", data["collar_type"]),
                ("CUTTING CELANA", data["pants_cutting"]),
                ("PROMO LOGO EZ", data.get("promo_logo_ez") or "N/A"),
                ("TAG SIZE - BAWAH BAJU", data.get("tag_size_bottom") or "N/A"),
                ("TAG SIZE - PUNDAK (DTF)", data.get("tag_size_shoulder") or "N/A"),
            ]
        ]
        s_table = Table(s_data, colWidths=[5.5 * cm, 4 * cm])
        s_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        left_story.append(s_table)
        left_story.append(Spacer(1, 0.5 * cm))

        # --- 5. BOTTOM LEFT LOGO ---
        real_path = media_to_path("/media/ez_full.png")
        img = Image(real_path, width=7.5 * cm, height=0.8 * cm)
        left_story.append(img)

        # === RIGHT COLUMN ===

        # --- 1. PREVIEW CETAK ---
        right_story.append(Paragraph("PREVIEW CETAK", styles["SectionTitle"]))
        # More placeholder cells
        pc_front_cell = [
            Spacer(1, 3 * cm),
            Paragraph(f"<i>(Preview Image 1)</i>", styles["Placeholder"]),
            Spacer(1, 3 * cm),
        ]
        pc_back_cell = [
            Spacer(1, 3 * cm),
            Paragraph(f"<i>(Preview Image 2)</i>", styles["Placeholder"]),
            Spacer(1, 3 * cm),
        ]
        pc_table = Table([[pc_front_cell, pc_back_cell]], colWidths=[5.5 * cm, 4 * cm])
        pc_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        right_story.append(pc_table)
        # right_story.append(Spacer(1, 0.5 * cm))

        # --- 2. LOGO ---
        right_story.append(Paragraph("LOGO", styles["SectionTitle"]))

        def create_logo_cell(title, json_key):
            val = data.get(json_key)

            # Convert media URL to real filesystem path
            real_path = media_to_path(val)

            elements = [Paragraph(title, styles["LogoTitle"]), Spacer(1, 0 * cm)]

            if real_path and os.path.exists(real_path):
                try:
                    img = Image(real_path, width=2.7 * cm, height=2.7 * cm)
                    elements.append(img)
                except Exception as e:
                    elements.append(
                        Paragraph(
                            f"<i>(Failed to load image: {e})</i>", styles["Placeholder"]
                        )
                    )
            else:
                placeholder_val = val if val else "N/A"
                elements.append(
                    Paragraph(f"<i>({placeholder_val})</i>", styles["Placeholder"])
                )

            elements.append(Spacer(1, 0.1 * cm))
            return elements

        l_cell_1 = create_logo_cell("DADA KANAN", "logo_chest_right")
        l_cell_2 = create_logo_cell("TENGAH", "logo_center")
        l_cell_3 = create_logo_cell("DADA KIRI", "logo_chest_left")
        l_cell_4 = create_logo_cell("BELAKANG", "logo_back")
        l_cell_5 = create_logo_cell("CELANA", "logo_pants")

        l_data = [[l_cell_1, l_cell_2, l_cell_3], [l_cell_4, l_cell_5, ""]]
        l_table = Table(
            l_data, colWidths=[3.16 * cm, 3.16 * cm, 3.16 * cm]
        )  # 8cm total
        l_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (0, 0), 1, colors.black),
                    ("BOX", (1, 0), (1, 0), 1, colors.black),
                    ("BOX", (2, 0), (2, 0), 1, colors.black),
                    ("BOX", (0, 1), (0, 1), 1, colors.black),
                    ("BOX", (1, 1), (1, 1), 1, colors.black),
                    ("BOX", (2, 1), (2, 1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        right_story.append(l_table)
        # right_story.append(Spacer(1, 0.5 * cm))

        # --- 3. QUALITY CONTROL ---
        right_story.append(Paragraph("QUALITY CONTROL", styles["SectionTitle"]))
        qc_data = [
            [Paragraph("<b>Desain:</b>", styles["Body"]), "-"],
            [Paragraph("<b>Print:</b>", styles["Body"]), "-"],
            [Paragraph("<b>Press:</b>", styles["Body"]), "-"],
            [Paragraph("<b>QC Line:</b>", styles["Body"]), "-"],
            [Paragraph("<b>QC Finishing:</b>", styles["Body"]), "-"],
        ]
        qc_table = Table(qc_data, colWidths=[4.5 * cm, 5 * cm], rowHeights=0.8 * cm)
        qc_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        right_story.append(qc_table)
        # right_story.append(Spacer(1, 0.5 * cm))

        # --- Build Main Table (2 Columns) ---
        # Total page width (A4) = 21cm. Margins = 1.5 + 1.5 = 3cm.
        # Drawable width = 18cm.
        main_layout_table = Table(
            [[left_story, right_story]],
            colWidths=[10 * cm, 10 * cm],  # 9.5 + 8.5 = 18cm
        )
        main_layout_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

        story.append(main_layout_table)

        # ==================================================================
        # === NEW: BUILD PAGE 2 ===
        # ==================================================================

        details_list = data.get("details", [])

        if details_list:
            story.append(PageBreak())

            # --- 1. Group Data ---
            grouped_details = {"PRIA": {}, "WANITA": {}, "ANAK": {}}

            for item in details_list:
                shirt_size = item.get("shirt_size", "UNKNOWN").upper()

                gender = "PRIA"  # Default
                if "WOMEN" in shirt_size:
                    gender = "WANITA"
                elif "KIDS" in shirt_size:
                    gender = "ANAK"

                size_str = (
                    shirt_size.replace("WOMEN", "")
                    .replace("KIDS", "")
                    .replace("MEN", "")
                    .strip()
                )
                size_key = f"SIZE {size_str}"  # e.g., "SIZE L"

                if size_key not in grouped_details[gender]:
                    grouped_details[gender][size_key] = []
                grouped_details[gender][size_key].append(item)

            # --- 2. Define Table Structure ---
            details_table_data = []
            table_style_commands = []

            # Page width 21cm - 2cm margins = 19cm drawable
            col_widths = [
                0.8 * cm,  # NO
                3 * cm,  # NAMA PUNGGUNG
                0.8 * cm,  # NO
                2.05 * cm,  # SIZE BAJU
                2.05 * cm,  # SIZE CELANA
                1 * cm,  # JUMLAH
                1.2 * cm,  # PRINT
                1.2 * cm,  # PRESS
                1.2 * cm,  # QC LINE
                1.25 * cm,  # POTONG
                1.2 * cm,  # JAHIT
                1.2 * cm,  # QC
                1.9 * cm,  # KET
            ]

            # --- 3. Add Header Row ---
            header_row = [
                Paragraph("NO", styles["H_DarkBlue"]),
                Paragraph("NAMA PUNGGUNG", styles["H_DarkBlue"]),
                Paragraph("NO", styles["H_DarkBlue"]),
                Paragraph("SIZE BAJU", styles["H_DarkBlue"]),
                Paragraph("SIZE CELANA", styles["H_DarkBlue"]),
                Paragraph("JML", styles["H_Black"]),
                Paragraph("PRINT", styles["H_Yellow"]),
                Paragraph("PRESS", styles["H_Yellow"]),
                Paragraph("QC LINE", styles["H_Yellow"]),
                Paragraph("POTONG", styles["H_Green"]),
                Paragraph("JAHIT", styles["H_Blue"]),
                Paragraph("QC", styles["H_Orange"]),
                Paragraph("KET", styles["H_Yellow"]),
            ]
            details_table_data.append(header_row)
            table_style_commands.append(("GRID", (0, 0), (-1, 0), 0.5, colors.black))
            table_style_commands.append(("VALIGN", (0, 0), (-1, 0), "MIDDLE"))
            # Remove padding for styled paragraphs
            table_style_commands.append(("LEFTPADDING", (0, 0), (-1, 0), 0))
            table_style_commands.append(("RIGHTPADDING", (0, 0), (-1, 0), 0))
            table_style_commands.append(("TOPPADDING", (0, 0), (-1, 0), 0))
            table_style_commands.append(("BOTTOMPADDING", (0, 0), (-1, 0), 0))

            # --- 4. Add Data Rows (Grouped) ---
            item_counter = 1
            gender_order = ["PRIA", "WANITA", "ANAK"]

            # Helper for sorting sizes
            def size_sort_key(size_name_key):  # e.g., "SIZE L"
                size = size_name_key.split(" ")[-1].upper()  # e.g., "L"
                order = ["S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"]
                if size in order:
                    return order.index(size)
                return len(order)  # Put unknowns at the end

            for gender in gender_order:
                gender_groups = grouped_details.get(gender)
                if not gender_groups:
                    continue

                current_row_index = len(details_table_data)

                # Add Gender Header Row
                gender_header_cell = Paragraph(gender, styles["HeaderGender"])
                details_table_data.append(
                    [gender_header_cell, "", "", "", "", "", "", "", "", "", "", "", ""]
                )

                # Add style for gender row
                table_style_commands.append(
                    ("SPAN", (0, current_row_index), (-1, current_row_index))
                )
                table_style_commands.append(
                    (
                        "BACKGROUND",
                        (0, current_row_index),
                        (0, current_row_index),
                        colors.HexColor("#90EE90"),
                    )
                )
                table_style_commands.append(
                    (
                        "GRID",
                        (0, current_row_index),
                        (-1, current_row_index),
                        0.5,
                        colors.black,
                    )
                )
                table_style_commands.append(
                    ("LEFTPADDING", (0, current_row_index), (-1, current_row_index), 0)
                )
                table_style_commands.append(
                    ("RIGHTPADDING", (0, current_row_index), (-1, current_row_index), 0)
                )
                table_style_commands.append(
                    ("TOPPADDING", (0, current_row_index), (-1, current_row_index), 0)
                )
                table_style_commands.append(
                    (
                        "BOTTOMPADDING",
                        (0, current_row_index),
                        (-1, current_row_index),
                        0,
                    )
                )

                sorted_size_keys = sorted(gender_groups.keys(), key=size_sort_key)

                for size_key in sorted_size_keys:
                    items = gender_groups[size_key]
                    if not items:
                        continue

                    num_items = len(items)
                    current_row_index = len(details_table_data)

                    # --- MODIFIED: Add Size Header Row as a FULL span ---
                    size_header_cell = Paragraph(size_key, styles["HeaderSize"])

                    # The total cell is no longer on this row
                    details_table_data.append(
                        [
                            size_header_cell,
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ]
                    )

                    # --- MODIFIED: Make the size row span ALL columns (-1) ---
                    table_style_commands.append(
                        ("SPAN", (0, current_row_index), (-1, current_row_index))
                    )
                    table_style_commands.append(
                        (
                            "GRID",
                            (0, current_row_index),
                            (-1, current_row_index),
                            0.5,
                            colors.black,
                        )
                    )
                    table_style_commands.append(
                        (
                            "VALIGN",
                            (0, current_row_index),
                            (-1, current_row_index),
                            "MIDDLE",
                        )
                    )
                    table_style_commands.append(
                        (
                            "LEFTPADDING",
                            (0, current_row_index),
                            (-1, current_row_index),
                            0,
                        )
                    )
                    table_style_commands.append(
                        (
                            "RIGHTPADDING",
                            (0, current_row_index),
                            (-1, current_row_index),
                            0,
                        )
                    )
                    table_style_commands.append(
                        (
                            "TOPPADDING",
                            (0, current_row_index),
                            (-1, current_row_index),
                            0,
                        )
                    )
                    table_style_commands.append(
                        (
                            "BOTTOMPADDING",
                            (0, current_row_index),
                            (-1, current_row_index),
                            0,
                        )
                    )

                    # --- MODIFIED: Add Item Rows, with 'JUMLAH' on the *first* item ---
                    for i, item in enumerate(items):
                        current_row_index_item = len(details_table_data)
                        is_first_item = i == 0

                        # --- NEW: Create total cell only for the first item ---
                        total_cell_content = ""
                        if is_first_item:
                            total_cell_content = Paragraph(
                                str(num_items), styles["TotalCell"]
                            )

                        row = [
                            Paragraph(str(item_counter), styles["BodyCellCenter"]),
                            Paragraph(
                                item.get("back_name", "TANPA NAMA"),
                                styles["BodyCellLeft"],
                            ),
                            Paragraph(
                                item.get("jersey_number", "00"),
                                styles["BodyCellCenter"],
                            ),
                            Paragraph(
                                item.get("shirt_size", ""), styles["BodyCellCenter"]
                            ),
                            Paragraph(
                                item.get("pants_size", ""), styles["BodyCellCenter"]
                            ),
                            # --- MODIFIED: Add the total cell here ---
                            total_cell_content,  # JUM-LAH
                            "",  # PRINT
                            "",  # PRESS
                            "",  # QC LINE
                            "",  # POTONG
                            "",  # JAHIT
                            "",  # QC
                            "",  # KET
                        ]
                        details_table_data.append(row)

                        # Apply grid to all cells
                        table_style_commands.append(
                            (
                                "GRID",
                                (0, current_row_index_item),
                                (-1, current_row_index_item),
                                0.5,
                                colors.black,
                            )
                        )
                        table_style_commands.append(
                            (
                                "VALIGN",
                                (0, current_row_index_item),
                                (-1, current_row_index_item),
                                "MIDDLE",
                            )
                        )

                        # --- NEW: Add ROWSPAN starting from this *first item row* ---
                        if is_first_item and num_items > 1:
                            row_start = current_row_index_item
                            # Span for num_items, so end row is start + num_items - 1
                            row_end = current_row_index_item + num_items - 1

                            # 1. Span the cell (col 5)
                            table_style_commands.append(
                                ("SPAN", (5, row_start), (5, row_end))
                            )

                            # 2. Vertically align the text
                            table_style_commands.append(
                                ("VALIGN", (5, row_start), (5, row_end), "MIDDLE")
                            )

                            # 3. Redraw the box for the spanned cell
                            table_style_commands.append(
                                ("BOX", (5, row_start), (5, row_end), 0.5, colors.black)
                            )

                        item_counter += 1

            # --- 5. Create and add the table to the story ---
            details_table = Table(
                details_table_data,
                colWidths=col_widths,
                repeatRows=1,  # Repeat the main header on new pages
            )

            details_table.setStyle(TableStyle(table_style_commands))
            story.append(details_table)

        # ---------- Build PDF ----------
        doc.build(story)
        # buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()

        filename = f"order_form_{order_item.subid}.pdf"

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
