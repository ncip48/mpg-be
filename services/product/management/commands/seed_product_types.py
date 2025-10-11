from django.core.management.base import BaseCommand
from services.product.models import ProductType  # adjust import path if needed

class Command(BaseCommand):
    help = "Seed initial ProductType data"

    def handle(self, *args, **options):
        data = [
            {"code": "JERGEN", "code_description": "Jersey General", "description": "Jersey"},
            {"code": "JERLPE", "code_description": "Jersey Lengan Pendek", "description": "Jersey Lengan Pendek"},
            {"code": "JERLPA", "code_description": "Jersey Lengan Panjang", "description": "Jersey Lengan Panjang"},
            {"code": "POLGEN", "code_description": "Polo General", "description": "Polo"},
            {"code": "POLLPA", "code_description": "Polo Lengan Panjang", "description": "Polo Lengan Panjang"},
            {"code": "POLCL1", "code_description": "Polo Classic 1", "description": "Polo Classic 1"},
            {"code": "POLCL2", "code_description": "Polo Classic 2", "description": "Polo Classic 2"},
            {"code": "BASEBA", "code_description": "Baseball", "description": "Baseball"},
            {"code": "CELGEN", "code_description": "Celana General", "description": "Celana"},
            {"code": "CELKAN", "code_description": "Celana Kantong", "description": "Celana Kantong"},
            {"code": "CELPAN", "code_description": "Celana Panjang", "description": "Celana Panjang"},
            {"code": "CELJOG", "code_description": "Celana Jogger", "description": "Celana Jogger"},
        ]

        created_count = 0
        for item in data:
            obj, created = ProductType.objects.get_or_create(
                code=item["code"],
                defaults={
                    "code_description": item["code_description"],
                    "description": item["description"],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seed completed: {created_count} ProductType(s) created."))
