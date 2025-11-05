from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.product.models.variant_type import ProductVariantType
from services.product.rest.variant_type.serializers import (
    ProductVariantTypeSerializer,
    ProductVariantTypeSerializerSimple,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ProductVariantTypeViewSet",)


class ProductVariantTypeViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Product Variant Types.
    Accessible only by superusers.
    """

    queryset = ProductVariantType.objects.all()
    serializer_class = ProductVariantTypeSerializer
    lookup_field = "subid"
    search_fields = ["name", "code"]
    required_perms = [
        "product.add_productvarianttype",
        "product.change_productvarianttype",
        "product.delete_productvarianttype",
        "product.view_productvarianttype",
    ]
    my_tags = ["Product Variant Types"]
    serializer_map = {
        "autocomplete": ProductVariantTypeSerializerSimple,
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        # Optional filter by product
        product_subid = self.request.query_params.get("product")
        if product_subid:
            queryset = queryset.filter(
                price_tiers__product__subid=product_subid
            ).distinct()

        return queryset
