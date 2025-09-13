from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import MainMembers, Elders
from .barcode_utils import generate_barcode_image, generate_8_digit_barcode

# List of titles eligible for barcodes
ELIGIBLE_TITLES = ['EVANGELIST', 'PASTOR', 'ELDER', 'MAMKHOKHELI']

@receiver(post_save, sender=MainMembers)
def create_barcode_for_eligible_member(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create barcodes when members with eligible titles are added or updated
    """
    # Check if this member has an eligible title and doesn't already have a barcode
    if instance.church_title in ELIGIBLE_TITLES and not Elders.objects.filter(branch_member_number=instance).exists():
        # Generate 8-digit numeric barcode
        barcode_value = generate_8_digit_barcode(instance)
        
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