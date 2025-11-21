from django.urls import include, path

from .print_verification import urls as print_verification_urls
from .qc_cutting_verification import urls as qc_cutting_verification_urls
from .qc_line_verification import urls as qc_line_verification_urls

app_name = "verification"

urlpatterns = [
    path("verification/", include(print_verification_urls)),
    path("verification/", include(qc_line_verification_urls)),
    path("verification/", include(qc_cutting_verification_urls)),
]
