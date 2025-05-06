from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
from .models import MainMembers, Elders
from .barcode_utils import generate_barcode_image

# List of titles eligible for barcodes
ELIGIBLE_TITLES = ['EVANGELIST', 'PASTOR', 'ELDER']

@receiver(post_save, sender=MainMembers)
def create_barcode_for_eligible_member(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create barcodes when members with eligible titles are added or updated
    """
    # Check if this member has an eligible title and doesn't already have a barcode
    if instance.church_title in ELIGIBLE_TITLES and not Elders.objects.filter(branch_member_number=instance).exists():
        # Generate prefix based on title (EV for EVANGELIST, PS for PASTOR, etc.)
        prefix = ''.join([word[0] for word in instance.church_title.split()]).upper()
        barcode_value = f"{prefix}-{instance.branch_member_number}-{uuid.uuid4().hex[:6].upper()}"
        
        # Generate barcode image
        barcode_image = generate_barcode_image(barcode_value)
        
        # Create elder record
        Elders.objects.create(
            branch_member_number=instance,
            title=instance.church_title,
            barcode_value=barcode_value,
            barcode_image=barcode_image,
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date().replace(year=timezone.now().year + 1),
            status='active'
        )