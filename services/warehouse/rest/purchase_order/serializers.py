from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.warehouse.models import PurchaseOrder
from services.warehouse.models.material import Material
from services.warehouse.models.supplier import Supplier
from services.warehouse.rest.material.serializers import MaterialSerializerSimple
from services.warehouse.rest.supplier.serializers import SupplierSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("PurchaseOrderSerializer",)


class PurchaseOrderSerializer(BaseModelSerializer):
    """
    Serializer for Finance Purchase Orders.
    """

    supplier = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Supplier.objects.all(),
        required=True,
    )

    material = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Material.objects.all(),
        required=True,
    )

    po_number = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrder
        fields = [
            "pk",
            "po_number",
            "supplier",
            "material",
            "qty_ordered",
            "order_date",
            "created_by",
            "created",
        ]
        read_only_fields = ["created_by", "created"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["supplier"] = SupplierSerializer(instance.supplier).data
        data["material"] = MaterialSerializerSimple(instance.material).data
        data["created_by"] = UserSerializerSimple(instance.created_by).data
        return data
