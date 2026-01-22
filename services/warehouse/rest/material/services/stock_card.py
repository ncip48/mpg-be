from django.db.models import F, Value, CharField, IntegerField
from django.db.models.functions import Cast, Concat
from django.utils.translation import gettext_lazy as _

from services.warehouse.models import Receiving, Issuing, StockOpname


class MaterialStockCardService:
    def __init__(self, material, start_date=None, end_date=None):
        self.material = material
        self.start_date = start_date
        self.end_date = end_date

    def _apply_date_filter(self, qs, field_name: str):
        if self.start_date:
            qs = qs.filter(**{f"{field_name}__gte": self.start_date})
        if self.end_date:
            qs = qs.filter(**{f"{field_name}__lte": self.end_date})
        return qs

    def get_history(self):
        # ======================
        # Receiving (IN)
        # ======================
        receivings = Receiving.objects.filter(
            purchase_order__material=self.material
        )
        receivings = self._apply_date_filter(receivings, "date_received")

        receivings = receivings.annotate(
            date=F("date_received"),
            activity=Value(_("Masuk (In)"), output_field=CharField()),
            description=F("purchase_order__supplier__name"),
            _qty_in=F("qty_received"),
            _qty_out=Value(0, output_field=IntegerField()),
        ).values(
            "date",
            "activity",
            "description",
            qty_in=F("_qty_in"),
            qty_out=F("_qty_out"),
        )

        # ======================
        # Issuing (OUT)
        # ======================
        issuings = Issuing.objects.filter(material=self.material)
        issuings = self._apply_date_filter(issuings, "date_out")

        issuings = issuings.annotate(
            date=F("date_out"),
            activity=Value(_("Keluar (Out)"), output_field=CharField()),
            description=Cast(F("forecast_date"), CharField()),
            _qty_in=Value(0, output_field=IntegerField()),
            _qty_out=F("qty_out"),
        ).values(
            "date",
            "activity",
            "description",
            "qty_out",
            qty_in=F("_qty_in"),
        )

        # ======================
        # Stock Opname (ADJUST)
        # ======================
        opnames = StockOpname.objects.filter(material=self.material)
        opnames = self._apply_date_filter(opnames, "date_so")

        opnames = opnames.annotate(
            date=F("date_so"),
            activity=Value(_("Stock Opname"), output_field=CharField()),
            description=Concat(
                Value("System: "),
                Cast(F("qty_system"), CharField()),
                Value(" -> Actual: "),
                Cast(F("qty_actual"), CharField()),
                output_field=CharField(),
            ),
            _qty_in=Value(0, output_field=IntegerField()),
            _qty_out=Value(0, output_field=IntegerField()),
        ).values(
            "date",
            "activity",
            "description",
            qty_in=F("_qty_in"),
            qty_out=F("_qty_out"),
        )

        # ======================
        # UNION (🔥 single SQL)
        # ======================
        return (
            receivings
            .union(issuings, opnames, all=True)
            .order_by("-date")
        )
