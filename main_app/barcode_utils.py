from django.utils import timezone
import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from .models import MainMembers, Elders

# Define eligible titles for barcode generation
ELIGIBLE_TITLES = ['EVANGELIST', 'OVERSEERER', 'REVEREND']

def generate_barcode_for_evangelists():
    """
    Find all members with eligible titles and create barcode entries for them in the Elders table
    """
    # Find all members with eligible titles
    members_with_titles = MainMembers.objects.filter(church_title__in=ELIGIBLE_TITLES)
    
    # Count of processed records
    created_count = 0
    
    for member in members_with_titles:
        # Check if this member already has a barcode in the Elders table
        if not Elders.objects.filter(branch_member_number=member).exists():
            # Generate prefix based on title (EV for EVANGELIST, OV for OVERSEER, etc.)
            prefix = ''.join([word[0] for word in member.church_title.split()]).upper()
            
            # Generate a unique barcode value
            barcode_value = f"{prefix}-{member.branch_member_number}-{uuid.uuid4().hex[:6].upper()}"
            
            # Generate barcode image
            barcode_image = generate_barcode_image(barcode_value)
            
            # Create new record in Elders table
            elder = Elders(
                branch_member_number=member,
                title=member.church_title,
                barcode_value=barcode_value,
                barcode_image=barcode_image,
                issue_date=timezone.now().date(),
                expiry_date=timezone.now().date().replace(year=timezone.now().year + 1),  # Valid for 1 year
                status='active'
            )
            elder.save()
            created_count += 1
    
    return created_count

def generate_barcode_image(barcode_value):
    """Generate a barcode image and return it as binary data"""
    # Create a Code128 barcode
    code128 = barcode.get('code128', barcode_value, writer=ImageWriter())
    
    # Save the barcode to a BytesIO object
    buffer = BytesIO()
    code128.write(buffer)
    
    # Get the binary data
    barcode_image = buffer.getvalue()
    buffer.close()
    
    return barcode_image
