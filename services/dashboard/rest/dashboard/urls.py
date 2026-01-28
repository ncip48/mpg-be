from services.dashboard.rest.dashboard.views import ForecastEstimateReminderView
from django.urls import path

from .views import (
    TotalForecastView,
    TotalDefectView,
    TotalOrderView,
    TotalComplaintView,
)

urlpatterns = [
    path("total-forecast/", TotalForecastView.as_view()),
    path("total-defect/", TotalDefectView.as_view()),
    path("total-order/", TotalOrderView.as_view()),
    path("total-complaint/", TotalComplaintView.as_view()),
    path("forecast-reminder/", ForecastEstimateReminderView.as_view()),
]
