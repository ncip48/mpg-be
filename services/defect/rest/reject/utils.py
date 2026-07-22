from services.defect.models import Reject
from django.contrib.contenttypes.models import ContentType

from django.contrib.contenttypes.models import ContentType

def sync_reject(verification, qty, note, user):
    content_type = ContentType.objects.get_for_model(verification)

    reject = Reject.objects.filter(
        content_type=content_type,
        object_id=verification.pk,
    ).first()

    # Rules 1 & 2
    if verification.is_approved:
        
        verification.error_from = None
        verification.save(update_fields=["error_from"])
        
        if reject:
            reject.delete()
        return

    # Rules 3 & 4
    if reject:
        reject.qty = qty
        reject.defect = note or ""
        reject.save(update_fields=["qty", "defect"])
    else:
        Reject.objects.create(
            content_type=content_type,
            object_id=verification.pk,
            qty=qty,
            defect=note or "",
            created_by=user,
        )
        
        
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