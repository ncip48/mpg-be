from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from core.common.paginations import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from core.common.permissions import HasRolePermission

User = get_user_model()

class BaseViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and managing superusers.
    Only accessible by superusers.
    Includes filter, search, ordering, and pagination.
    """
    permission_classes = [IsAuthenticated, HasRolePermission]

    # Enable filtering, searching, ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # ✅ Filtering by fields
    filterset_fields = []

    # ✅ Searching (case-insensitive)
    search_fields = []

    # ✅ Ordering
    ordering_fields = ["created"]
    ordering = ["-created"]
    
    # ✅ Pagination
    pagination_class = PageNumberPagination
    
    serializer_map = None

    def get_serializer_class(self):
        serializer = None
        if self.serializer_map is not None:
            serializer = self.serializer_map.get(self.action, None)

        if serializer is None:
            serializer = super().get_serializer_class()
        return serializer
    
    def autocomplete(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
