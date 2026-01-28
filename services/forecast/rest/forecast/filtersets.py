import django_filters
from services.forecast.rest.forecast.filters.mixins import PrinterFabricBaseFilterSet

from services.forecast.models import Forecast


class ForecastFilterSet(PrinterFabricBaseFilterSet):
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

    # priority_status = django_filters.CharFilter(
    #     field_name="priority_status", lookup_expr="exact"
    # )

    sewer = django_filters.CharFilter(
        field_name="sewer_distributions__sewer__subid", lookup_expr="exact"
    )

    # # Print verification
    # is_approved = django_filters.BooleanFilter(
    #     field_name="print_verifications__is_approved", lookup_expr="exact"
    # )

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
            # "priority_status",
            # "type",
            # "is_approved",
            "sewer",
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
