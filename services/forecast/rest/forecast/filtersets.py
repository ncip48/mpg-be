import django_filters
from django.db.models import Q

from services.forecast.models import Forecast


class ForecastFilterSet(django_filters.FilterSet):
    is_print = django_filters.BooleanFilter(field_name="print_status")
    print_status = django_filters.BooleanFilter(field_name="print_status")
    has_qc_finishing = django_filters.BooleanFilter(
        method="filter_has_qc_finishing",
        label="Has QC Finishing",
    )
    has_qc_finishing_defect = django_filters.BooleanFilter(
        method="filter_has_qc_finishing_defect",
        label="Has QC Finishing Defect",
    )
    has_qc_cutting_verification = django_filters.BooleanFilter(
        method="filter_has_qc_cutting_verification",
        label="Has QC Cutting Verification",
    )
    has_qc_line_verification = django_filters.BooleanFilter(
        method="filter_has_qc_line_verification",
        label="Has QC Line Verification",
    )
    has_print_verification = django_filters.BooleanFilter(
        method="filter_has_print_verification",
        label="Has Print Verification",
    )
    has_warehouse_delivery = django_filters.BooleanFilter(
        method="filter_has_warehouse_delivery",
        label="Has QC Warehouse Delivery",
    )
    has_warehouse_receipt = django_filters.BooleanFilter(
        method="filter_has_warehouse_receipt",
        label="Has QC Warehouse Delivery",
    )

    priority_status = django_filters.CharFilter(
        field_name="priority_status", lookup_expr="exact"
    )
    printer = django_filters.CharFilter(method="filter_printer")
    fabric_type = django_filters.CharFilter(method="filter_fabric_type")

    type = django_filters.CharFilter(
        method="filter_type",
        label="Type",
    )

    # Print verification
    is_approved = django_filters.BooleanFilter(
        field_name="print_verifications__is_approved", lookup_expr="exact"
    )

    class Meta:
        model = Forecast
        fields = [
            "is_print",
            "print_status",
            "has_qc_finishing",
            "has_qc_finishing_defect",
            "has_qc_cutting_verification",
            "has_qc_line_verification",
            "has_print_verification",
            "has_warehouse_delivery",
            "has_warehouse_receipt",
            "priority_status",
            "printer",
            "fabric_type",
            "type",
            "is_approved",
        ]

    def filter_has_qc_finishing(self, queryset, name, value):
        """
        value = True  -> Forecast WITH QCFinishing
        value = False -> Forecast WITHOUT QCFinishing
        """
        if value is True:
            return queryset.filter(qc_finishings__isnull=False)
        if value is False:
            return queryset.filter(qc_finishings__isnull=True)

        return queryset

    def filter_has_qc_finishing_defect(self, queryset, name, value):
        """
        value = True  -> Forecast WITH QCFinishingDefect
        value = False -> Forecast WITHOUT QCFinishingDefect
        """
        if value is True:
            return queryset.filter(qc_finishing_defects__isnull=False)
        if value is False:
            return queryset.filter(qc_finishing_defects__isnull=True)

        return queryset

    def filter_has_qc_cutting_verification(self, queryset, name, value):
        """
        value = True  -> Forecast WITH
        value = False -> Forecast WITHOUT
        """
        if value is True:
            return queryset.filter(qc_cutting_verifications__isnull=False)
        if value is False:
            return queryset.filter(qc_cutting_verifications__isnull=True)

        return queryset

    def filter_has_qc_line_verification(self, queryset, name, value):
        """
        value = True  -> Forecast WITH
        value = False -> Forecast WITHOUT
        """
        if value is True:
            return queryset.filter(qc_line_verifications__isnull=False)
        if value is False:
            return queryset.filter(qc_line_verifications__isnull=True)

        return queryset

    def filter_has_print_verification(self, queryset, name, value):
        """
        value = True  -> Forecast WITH
        value = False -> Forecast WITHOUT
        """
        if value is True:
            return queryset.filter(print_verifications__isnull=False)
        if value is False:
            return queryset.filter(print_verifications__isnull=True)

        return queryset

    def filter_has_warehouse_delivery(self, queryset, name, value):
        """
        value = True  -> Forecast WITH
        value = False -> Forecast WITHOUT
        """
        if value is True:
            return queryset.filter(warehouse_deliveries__isnull=False)
        if value is False:
            return queryset.filter(warehouse_deliveries__isnull=True)

        return queryset

    def filter_has_warehouse_receipt(self, queryset, name, value):
        """
        value = True  -> Forecast WITH
        value = False -> Forecast WITHOUT
        """
        if value is True:
            return queryset.filter(warehouse_receipts__isnull=False)
        if value is False:
            return queryset.filter(warehouse_receipts__isnull=True)

        return queryset

    def filter_type(self, queryset, name, value):
        if value == "stock":
            return queryset.filter(is_stock=True)
        if value == "konveksi":
            return queryset.filter(order__order_type="konveksi")
        if value == "marketplace":
            return queryset.filter(order__order_type="marketplace")

        return queryset

    def filter_printer(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            # 1️⃣ stock
            Q(
                is_stock=True,
                stock_items__product__printer__subid=value,
            )
            |
            # 2️⃣ non-stock with order_item
            Q(
                is_stock=False,
                order_item__isnull=False,
                order_item__product__printer__subid=value,
            )
            |
            # 3️⃣ non-stock without order_item → OrderForm
            Q(
                is_stock=False,
                order_item__isnull=True,
                order__order_forms__printer__subid=value,
            )
        ).distinct()

    def filter_fabric_type(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            # 1️⃣ stock
            Q(
                is_stock=True,
                stock_items__fabric_type__subid=value,
            )
            |
            # 2️⃣ non-stock with order_item
            Q(
                is_stock=False,
                order_item__isnull=False,
                order_item__fabric_type__subid=value,
            )
            |
            # 3️⃣ non-stock without order_item → OrderForm
            Q(
                is_stock=False,
                order_item__isnull=True,
                order__order_forms__fabric_type__subid=value,
            )
        ).distinct()
