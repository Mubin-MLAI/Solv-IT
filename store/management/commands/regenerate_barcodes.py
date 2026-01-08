"""
Management command to generate/regenerate barcodes for products.

Usage:
    python manage.py regenerate_barcodes              # Regenerate for products without barcodes
    python manage.py regenerate_barcodes --all        # Regenerate for all products
    python manage.py regenerate_barcodes --serial ABC123  # Regenerate for specific serial
"""

from django.core.management.base import BaseCommand, CommandError
from store.models import Item
from store.barcode_utils import generate_barcode_file
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate or regenerate barcodes for products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerate barcodes for all products',
        )
        parser.add_argument(
            '--serial',
            type=str,
            help='Regenerate barcode for specific serial number',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('🔄 Starting barcode regeneration...\n'))
            
            if options['serial']:
                # Regenerate for specific serial
                serial = options['serial']
                self.stdout.write(f"🔍 Searching for product with serial: {serial}")
                
                try:
                    item = Item.objects.get(serialno__iexact=serial)
                    self._generate_barcode_for_item(item)
                except Item.DoesNotExist:
                    raise CommandError(f"❌ Product with serial '{serial}' not found")
            
            elif options['all']:
                # Regenerate for all products
                self.stdout.write(self.style.WARNING('\n⚠️ Regenerating barcodes for ALL products...\n'))
                items = Item.objects.all()
                self._regenerate_for_items(items)
            
            else:
                # Regenerate for products without barcodes
                self.stdout.write('🔄 Regenerating barcodes for products without barcodes...\n')
                items = Item.objects.filter(barcode_file__isnull=True) | Item.objects.filter(barcode_file='')
                
                if not items.exists():
                    self.stdout.write(self.style.SUCCESS('✅ All products already have barcodes!'))
                    return
                
                self._regenerate_for_items(items)
        
        except Exception as e:
            raise CommandError(f"❌ Error: {str(e)}")

    def _regenerate_for_items(self, items):
        """Regenerate barcodes for multiple items"""
        total = items.count()
        self.stdout.write(f"📦 Found {total} product(s) to process\n")
        
        success_count = 0
        error_count = 0
        
        for index, item in enumerate(items, 1):
            try:
                self.stdout.write(f"\n[{index}/{total}] Processing: {item.name} (Serial: {item.serialno})")
                self._generate_barcode_for_item(item)
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ❌ Error: {str(e)}"))
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully generated: {success_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Failed: {error_count}'))
        self.stdout.write('='*70)

    def _generate_barcode_for_item(self, item):
        """Generate barcode for a single item"""
        if not item.serialno:
            raise ValueError(f"Item {item.name} has no serial number")
        
        try:
            serialno = item.serialno.strip()
            self.stdout.write(f"  🏷️ Serial: {serialno}")
            
            # Generate barcode
            barcode_filename, barcode_path = generate_barcode_file(serialno)
            
            # Update item
            item.barcode_file = barcode_path
            item.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'  ✅ Barcode generated: {barcode_filename}'
            ))
            
        except Exception as e:
            raise Exception(f"Barcode generation failed for {item.serialno}: {str(e)}")
