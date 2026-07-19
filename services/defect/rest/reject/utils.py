from services.defect.models import Reject
from django.contrib.contenttypes.models import ContentType

def sync_reject(verification, qty, note, user):
    if verification.is_approved:
        Reject.objects.filter(source=verification).delete()
        return

    reject, created = Reject.objects.update_or_create(
        content_type=ContentType.objects.get_for_model(verification),
        object_id=verification.pk,
        defaults={
            "qty": qty,
            "defect": note or "",
        },
    )

    if created:
        reject.created_by = user
        reject.save(update_fields=["created_by"])
        
        
def sync_reject_manual(verification, qty, note, user):
    reject, created = Reject.objects.update_or_create(
        content_type=ContentType.objects.get_for_model(verification),
        object_id=verification.pk,
        defaults={
            "qty": qty,
            "defect": note or "",
        },
    )

    if created:
        reject.created_by = user
        reject.save(update_fields=["created_by"])