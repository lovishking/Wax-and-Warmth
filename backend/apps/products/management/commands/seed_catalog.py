import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Import the original checked-in catalog into the database once.'

    def handle(self, *args, **options):
        catalog_path = Path(__file__).resolve().parents[2] / 'data' / 'legacy_catalog.json'
        products = json.loads(catalog_path.read_text(encoding='utf-8'))
        created = 0
        existing = 0
        for entry in products:
            category_name = entry['category'].replace('_', ' ').title()
            category, _ = Category.objects.get_or_create(name=category_name)
            _, was_created = Product.objects.get_or_create(
                slug=slugify(entry['name']),
                defaults={
                    'name': entry['name'],
                    'description': entry['description'],
                    'price': entry['price'],
                    'category': category,
                    'scent_family': 'SWEET' if entry['category'] == 'latte' else 'FLORAL',
                    'image': entry['image'],
                    'is_active': True,
                    'is_featured': entry['featured'],
                },
            )
            created += int(was_created)
            existing += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f'Catalog import complete: {created} created, {existing} already present. '
            'Products start with zero stock; add inventory from the admin panel.'
        ))
