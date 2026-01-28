from datetime import datetime, time

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
