from core.common.paginations import PageNumberPagination
from datetime import timedelta
from datetime import date

from django.db.models import F, ExpressionWrapper, IntegerField

from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from services.forecast.models import Forecast
from services.verification.models import QCFinishingDefect
from services.order.models import Order
from services.ticket.models import ComplaintTicket


def apply_date_filter(queryset, field_name, request):
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    filters = {}

    if start_date:
        filters[f"{field_name}__date__gte"] = parse_date(start_date)

    if end_date:
        filters[f"{field_name}__date__lte"] = parse_date(end_date)

    return queryset.filter(**filters)


class TotalForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Forecast.objects.all()
        qs = apply_date_filter(qs, "date_forecast", request)

        return Response({"count": qs.count()})


class TotalDefectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = QCFinishingDefect.objects.all()
        qs = apply_date_filter(qs, "created", request)

        return Response({"count": qs.count()})


class TotalOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Order.objects.all()
        qs = apply_date_filter(qs, "created", request)

        return Response({"count": qs.count()})


class TotalComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ComplaintTicket.objects.all()
        qs = apply_date_filter(qs, "received_date", request)

        return Response({"count": qs.count()})


class ForecastEstimateReminderView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        today = date.today()
        days_limit = int(request.query_params.get("days", 3))

        qs = Forecast.objects.filter(
            estimate_sent__isnull=False,
            estimate_sent__gte=today,
            estimate_sent__lte=today + timedelta(days=days_limit),
        ).order_by("estimate_sent")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)

        data = []
        for f in page:
            remaining_days = (f.estimate_sent - today).days

            data.append(
                {
                    "pk": f.subid,
                    "forecast_number": f.forecast_number,
                    "estimate_sent": f.estimate_sent,
                    "remaining_days": remaining_days,
                    "message": f"{remaining_days} Hari tersisa",
                }
            )

        return paginator.get_paginated_response(data)
