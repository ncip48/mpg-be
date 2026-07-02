from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QueueEntryViewSet

# --- Router for ViewSets ---
router = DefaultRouter()
router.register(r"queue-entries", QueueEntryViewSet, basename="queue-entries")
# --- End Router ---

urlpatterns = [
    path("", include(router.urls)),
]
