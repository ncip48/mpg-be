from django.urls import path

from .views import TrackingAPIView

urlpatterns = [
    path("order/", TrackingAPIView.as_view(), name="tracking-order"),
]