from rest_framework.routers import DefaultRouter

from services.ticket.rest.complaint.views import (
    ComplaintActionViewSet,
    ComplaintTicketViewSet,
)

router = DefaultRouter()
router.register(
    r"complaint-tickets",
    ComplaintTicketViewSet,
    basename="complaint-ticket",
)
router.register(
    r"complaint-actions",
    ComplaintActionViewSet,
    basename="complaint-action",
)

urlpatterns = router.urls
