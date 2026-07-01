from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from services.deposit.models import Deposit
from services.order.models import Invoice


class Command(BaseCommand):
    help = "Generate deposit invoices for deposits that don't already have one."

    @transaction.atomic
    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        deposits = Deposit.objects.prefetch_related("invoice")

        for deposit in deposits:
            # Skip if invoice already exists
            if hasattr(deposit, "invoice"):
                skipped_count += 1
                continue

            today = timezone.now().date()
            delivery_date = getattr(deposit, "delivery_date", today)

            invoice_no = (
                f"DEPOSIT.{today.year}.{today.month:02d}.{deposit.pk:05d}"
            )

            Invoice.objects.create(
                deposit=deposit,
                status="partial",
                invoice_no=invoice_no,
                issued_date=today,
                delivery_date=delivery_date,
                is_deposit_invoice=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created: {created_count}, Skipped: {skipped_count}"
            )
        )