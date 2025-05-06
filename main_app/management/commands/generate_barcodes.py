from django.core.management.base import BaseCommand
from main_app.barcode_utils import generate_barcode_for_evangelists

class Command(BaseCommand):
    help = 'Generate barcodes for members with EVANGELIST title'

    def handle(self, *args, **options):
        count = generate_barcode_for_evangelists()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} barcode entries for evangelists')
        )
