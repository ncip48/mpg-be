from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # kalau ada pk, isi dengan instance.subid
        if "pk" in data and hasattr(instance, "subid"):
            data["pk"] = str(instance.subid)  # pastikan string (UUID dsb)

        return data

    class Meta:
        abstract = True
