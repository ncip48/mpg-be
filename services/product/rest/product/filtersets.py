import django_filters

from services.product.models import Product


class ProductFilterSet(django_filters.FilterSet):
    # ForeignKey → filter by subid
    printer = django_filters.CharFilter(
        field_name="printer__subid", lookup_expr="exact"
    )

    store = django_filters.CharFilter(field_name="store__subid", lookup_expr="exact")

    class Meta:
        model = Product
        fields = [
            "printer",
            "store",
        ]
