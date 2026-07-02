from django.urls import include, path

from .queue_entry import urls as queue_entry_urls

app_name = "sewer"

urlpatterns = [
    path("queue-entry/", include(queue_entry_urls)),
]
