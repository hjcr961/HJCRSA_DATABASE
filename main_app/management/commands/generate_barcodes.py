from django.core.management.base import BaseCommand
from main_app.barcode_utils import generate_barcode_for_evangelists, recreate_all_barcodes

class Command(BaseCommand):
    help = 'Generate barcodes for members with eligible titles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Recreate all existing barcodes for eligible members',
        )

    def handle(self, *args, **options):
        if options['recreate']:
            count = recreate_all_barcodes()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully recreated {count} barcode entries for all eligible members')
            )
        else:
            count = generate_barcode_for_evangelists()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {count} new barcode entries for eligible members')
            )
