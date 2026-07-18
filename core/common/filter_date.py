from django.utils.dateparse import parse_date

def apply_date_filter(queryset, field_name, request):
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    filters = {}

    if start_date:
        filters[f"{field_name}__gte"] = parse_date(start_date)

    if end_date:
        filters[f"{field_name}__lte"] = parse_date(end_date)

    return queryset.filter(**filters)


def apply_forecast_date_filter(queryset, field_name, request):
    start_date = request.query_params.get("forecast_start_date")
    end_date = request.query_params.get("forecast_end_date")

    filters = {}

    if start_date:
        filters[f"{field_name}__gte"] = parse_date(start_date)

    if end_date:
        filters[f"{field_name}__lte"] = parse_date(end_date)

    return queryset.filter(**filters)

def apply_sewer_distribution_date_filter(queryset, field_name, request):
    start_date = request.query_params.get("sewer_distribution_start_date")
    end_date = request.query_params.get("sewer_distribution_end_date")

    filters = {}

    if start_date:
        filters[f"{field_name}__gte"] = parse_date(start_date)

    if end_date:
        filters[f"{field_name}__lte"] = parse_date(end_date)

    return queryset.filter(**filters)