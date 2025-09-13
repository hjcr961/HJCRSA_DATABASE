from django.utils import timezone
import random
import re
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from .models import MainMembers, Elders

# Define eligible titles for barcode generation
ELIGIBLE_TITLES = ['EVANGELIST', 'OVERSEERER', 'REVEREND', 'MAMKHOKHELI']

def generate_8_digit_barcode(member):
    """
    Generate an 8-digit numeric barcode for a member
    Priority: card_number > branch_member_number digits > random
    """
    # Try to use card_number first
    if member.card_number:
        # Convert card_number to string and pad to 8 digits
        base_number = str(member.card_number).zfill(8)
        
        # If it's already 8 digits or less, use it
        if len(base_number) <= 8:
            candidate = base_number[-8:]  # Take last 8 digits if longer
        else:
            # If card_number is longer than 8 digits, take the last 8
            candidate = base_number[-8:]
    else:
        # Fallback to branch_member_number - extract digits only
        branch_digits = re.sub(r'\D', '', member.branch_member_number or '')
        if branch_digits:
            candidate = branch_digits.zfill(8)[-8:]  # Pad and take last 8
        else:
            # Last resort: generate random 8-digit number
            candidate = str(random.randint(10000000, 99999999))
    
    # Ensure uniqueness
    original_candidate = candidate
    counter = 1
    while Elders.objects.filter(barcode_value=candidate).exists():
        # If conflict, modify the last few digits
        if len(original_candidate) == 8:
            # Replace last 2 digits with counter-based number
            base = original_candidate[:6]
            suffix = str(counter).zfill(2)
            candidate = base + suffix
            counter += 1
            if counter > 99:  # Prevent infinite loop
                candidate = str(random.randint(10000000, 99999999))
                break
        else:
            candidate = str(random.randint(10000000, 99999999))
            break
    
    return candidate

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
            # Generate 8-digit numeric barcode
            barcode_value = generate_8_digit_barcode(member)
            
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

def recreate_all_barcodes():
    """
    Recreate all existing barcodes for eligible members
    This will delete existing barcodes and create new ones
    """
    # Find all members with eligible titles
    members_with_titles = MainMembers.objects.filter(church_title__in=ELIGIBLE_TITLES)
    
    # Count of processed records
    recreated_count = 0
    
    for member in members_with_titles:
        # Delete existing barcode if it exists
        Elders.objects.filter(branch_member_number=member).delete()
        
        # Generate new 8-digit numeric barcode
        barcode_value = generate_8_digit_barcode(member)
        
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
        recreated_count += 1
    
    return recreated_count

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
