from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.defect.models import Reject
from services.order.rest.order.serializers import FloatToIntRepresentationMixin

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("RejectSerializer",)


class RejectSerializer(FloatToIntRepresentationMixin, BaseModelSerializer):
    """
    Serializer for Reject management.
    """
    float_to_int_fields = ["hpp"]

    source_type = serializers.SerializerMethodField()

    class Meta:
        model = Reject
        fields = [
            "pk",
            "source_type",
            "content_type",
            "object_id",
            "qty",
            "defect",
            "hpp",
            "note",
            "created_by",
            "created",
            "updated",
        ]
        read_only_fields = [
            "pk",
            "subid",
            "source_type",
            "created_by",
            "created",
            "updated",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        source_type_display = {
            "printverification": "Verifikasi Print",
            "qcpressverification": "QC Press",
            "qclineverification": "QC Line",
            "qccuttingverification": "QC Cutting",
            "qcfinishing": "QC Finishing",
            "qcfinishingdefect": "QC Finishing",
            "warehousedelivery": "Pengiriman Gudang",
            "warehousereceipt": "Penerimaan Gudang",
        }

        if instance.created_by:
            data["created_by"] = {
                "pk": instance.created_by.subid,
                "first_name": instance.created_by.first_name,
                "last_name": instance.created_by.last_name,
                "email": instance.created_by.email,
            }
        else:
            data["created_by"] = None

        # Optional: expose the referenced object
        if instance.source:
            source_type = instance.content_type.model
            
            data["source"] = {
                "type": instance.content_type.model,
                "type_display": source_type_display.get(source_type, source_type),
                "pk": instance.source.subid,
                "display": str(instance.source),
            }
        else:
            data["source"] = None

        return data

    def get_source_type(self, obj):
        return obj.content_type.model if obj.content_type else None