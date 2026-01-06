import django_filters

from services.ticket.models import ComplaintTicket


class ComplaintTicketFilterSet(django_filters.FilterSet):
    # ForeignKey → filter by subid
    order = django_filters.CharFilter(field_name="order__subid", lookup_expr="exact")

    created_by = django_filters.CharFilter(
        field_name="created_by__subid", lookup_expr="exact"
    )

    # Choice fields
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    complaint_type = django_filters.CharFilter(
        field_name="complaint_type", lookup_expr="exact"
    )

    customer_request = django_filters.CharFilter(
        field_name="customer_request", lookup_expr="exact"
    )

    class Meta:
        model = ComplaintTicket
        fields = [
            "order",
            "created_by",
            "status",
            "complaint_type",
            "customer_name",
        ]
