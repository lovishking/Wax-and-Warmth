"""
Management command to seed the database with sample candle products.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
from apps.products.models import Category, Product
from apps.products.services import FACET_FIELDS, set_product_facets
from apps.inventory.models import Inventory
from apps.recommendations.services import RAGService

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample candle products and categories'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Seed an admin only when explicit deployment-specific credentials exist.
        admin_email = os.environ.get('SEED_ADMIN_EMAIL', '').strip().lower()
        admin_password = os.environ.get('SEED_ADMIN_PASSWORD', '')
        if admin_email and admin_password and not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create_superuser(
                email=admin_email,
                username=admin_email.split('@')[0],
                password=admin_password,
                first_name='Store',
                last_name='Admin',
                role='ADMIN',
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.email}'))

        # Create categories
        categories_data = [
            {'name': 'Floral', 'description': 'Floral candles with flower-based fragrances'},
            {'name': 'Woody', 'description': 'Rich woody and earthy candle scents'},
            {'name': 'Fresh', 'description': 'Clean and refreshing candle fragrances'},
            {'name': 'Sweet', 'description': 'Sweet and indulgent candle scents'},
            {'name': 'Spicy', 'description': 'Warm and spicy candle fragrances'},
            {'name': 'Citrus', 'description': 'Bright and citrusy candle scents'},
            {'name': 'Oriental', 'description': 'Exotic and luxurious oriental fragrances'},
            {'name': 'Seasonal', 'description': 'Limited edition seasonal candles'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat.name] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')

        # Create products
        products_data = [
            {
                'name': 'Lavender Bliss',
                'description': 'A soft floral candle designed for a relaxing atmosphere. The gentle lavender is complemented by warm cedar undertones and a whisper of vanilla, creating an ideal environment for unwinding after a long day.',
                'price': 799,
                'category': categories['Floral'],
                'scent_family': 'FLORAL',
                'scent_notes': 'Lavender, Cedar, Vanilla',
                'fragrance_strength': 'MEDIUM',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Relaxing, Calm, Cozy',
                'recommended_rooms': 'Bedroom, Living Room',
                'recommended_occasions': 'Relaxation, Self-care, Evening',
                'is_featured': True,
            },
            {
                'name': 'Vanilla Cedar',
                'description': 'Warm vanilla perfectly balanced with woody cedar notes. This candle delivers a cozy, comforting atmosphere without being overly sweet. A perfect companion for quiet evenings.',
                'price': 799,
                'category': categories['Woody'],
                'scent_family': 'WOODY',
                'scent_notes': 'Vanilla, Cedar, Sandalwood',
                'fragrance_strength': 'MEDIUM',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Cozy, Warm, Comforting',
                'recommended_rooms': 'Bedroom, Living Room',
                'recommended_occasions': 'Evening, Relaxation, Gift',
                'is_featured': True,
            },
            {
                'name': 'Amber Sandalwood',
                'description': 'A rich, sophisticated blend of amber and sandalwood. Deep and luxurious, this candle creates an atmosphere of refined elegance. Perfect for those who appreciate a warm, enveloping fragrance.',
                'price': 899,
                'category': categories['Oriental'],
                'scent_family': 'ORIENTAL',
                'scent_notes': 'Amber, Sandalwood, Musk',
                'fragrance_strength': 'STRONG',
                'size': 'LARGE',
                'burn_time': '60-70 hours',
                'mood': 'Luxurious, Warm, Romantic',
                'recommended_rooms': 'Living Room, Bedroom',
                'recommended_occasions': 'Evening, Romance, Gift',
                'is_featured': True,
            },
            {
                'name': 'Rose Garden',
                'description': 'A delicate and romantic rose candle with hints of peony and white musk. Captures the essence of a blooming garden in full spring. Elegant and feminine.',
                'price': 849,
                'category': categories['Floral'],
                'scent_family': 'FLORAL',
                'scent_notes': 'Rose, Peony, White Musk',
                'fragrance_strength': 'MEDIUM',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Romantic, Elegant, Feminine',
                'recommended_rooms': 'Bedroom, Bathroom',
                'recommended_occasions': 'Romance, Gift, Self-care',
                'is_featured': True,
            },
            {
                'name': 'Ocean Breeze',
                'description': 'A clean, refreshing candle that captures the essence of a coastal morning. Sea salt, aquatic notes, and a hint of driftwood create a revitalizing atmosphere.',
                'price': 699,
                'category': categories['Fresh'],
                'scent_family': 'FRESH',
                'scent_notes': 'Sea Salt, Aquatic, Driftwood',
                'fragrance_strength': 'LIGHT',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Refreshing, Clean, Energizing',
                'recommended_rooms': 'Bathroom, Office, Living Room',
                'recommended_occasions': 'Morning, Work, Everyday',
                'is_featured': False,
            },
            {
                'name': 'Cinnamon Spice',
                'description': 'A warm, inviting blend of cinnamon, clove, and nutmeg. Reminiscent of a cozy kitchen during the holidays. Perfect for creating a festive atmosphere.',
                'price': 749,
                'category': categories['Spicy'],
                'scent_family': 'SPICY',
                'scent_notes': 'Cinnamon, Clove, Nutmeg',
                'fragrance_strength': 'STRONG',
                'size': 'MEDIUM',
                'burn_time': '35-45 hours',
                'mood': 'Warm, Festive, Cozy',
                'recommended_rooms': 'Kitchen, Living Room',
                'recommended_occasions': 'Holiday, Evening, Gathering',
                'is_featured': False,
            },
            {
                'name': 'Citrus Sunrise',
                'description': 'A bright and energizing candle with notes of lemon, bergamot, and grapefruit. Perfect for starting your morning with a burst of freshness.',
                'price': 649,
                'category': categories['Citrus'],
                'scent_family': 'CITRUS',
                'scent_notes': 'Lemon, Bergamot, Grapefruit',
                'fragrance_strength': 'MEDIUM',
                'size': 'SMALL',
                'burn_time': '25-30 hours',
                'mood': 'Energizing, Fresh, Uplifting',
                'recommended_rooms': 'Kitchen, Bathroom, Office',
                'recommended_occasions': 'Morning, Work, Everyday',
                'is_featured': False,
            },
            {
                'name': 'Midnight Jasmine',
                'description': 'An intoxicating blend of jasmine and ylang-ylang with a base of dark vanilla. Mysterious and seductive, perfect for quiet evening moments.',
                'price': 999,
                'category': categories['Floral'],
                'scent_family': 'FLORAL',
                'scent_notes': 'Jasmine, Ylang-Ylang, Dark Vanilla',
                'fragrance_strength': 'STRONG',
                'size': 'LARGE',
                'burn_time': '60-70 hours',
                'mood': 'Romantic, Mysterious, Luxurious',
                'recommended_rooms': 'Bedroom',
                'recommended_occasions': 'Romance, Evening, Special Occasion',
                'is_featured': True,
            },
            {
                'name': 'Forest Walk',
                'description': 'An earthy, grounding candle with pine, eucalyptus, and moss notes. Like walking through a misty forest at dawn. Perfect for meditation and mindfulness.',
                'price': 849,
                'category': categories['Woody'],
                'scent_family': 'WOODY',
                'scent_notes': 'Pine, Eucalyptus, Moss',
                'fragrance_strength': 'MEDIUM',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Grounding, Calm, Natural',
                'recommended_rooms': 'Living Room, Study',
                'recommended_occasions': 'Meditation, Yoga, Morning',
                'is_featured': False,
            },
            {
                'name': 'Honey Almond',
                'description': 'A sweet and comforting blend of golden honey, toasted almond, and warm milk. Like a warm treat on a cold evening. Indulgent without being overwhelming.',
                'price': 749,
                'category': categories['Sweet'],
                'scent_family': 'SWEET',
                'scent_notes': 'Honey, Toasted Almond, Warm Milk',
                'fragrance_strength': 'MEDIUM',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Comforting, Sweet, Cozy',
                'recommended_rooms': 'Kitchen, Bedroom, Living Room',
                'recommended_occasions': 'Evening, Relaxation, Gift',
                'is_featured': False,
            },
            {
                'name': 'Patchouli Noir',
                'description': 'A deep, earthy candle with patchouli, vetiver, and black pepper. Bold and unconventional, for those who prefer complex, character-driven fragrances.',
                'price': 949,
                'category': categories['Oriental'],
                'scent_family': 'EARTHY',
                'scent_notes': 'Patchouli, Vetiver, Black Pepper',
                'fragrance_strength': 'STRONG',
                'size': 'LARGE',
                'burn_time': '55-65 hours',
                'mood': 'Bold, Earthy, Sophisticated',
                'recommended_rooms': 'Living Room, Study',
                'recommended_occasions': 'Evening, Meditation, Special Occasion',
                'is_featured': False,
            },
            {
                'name': 'White Tea & Sage',
                'description': 'A clean and zen-like candle with white tea, sage, and fresh linen notes. Minimalist and calming, perfect for creating a spa-like experience at home.',
                'price': 799,
                'category': categories['Fresh'],
                'scent_family': 'HERBAL',
                'scent_notes': 'White Tea, Sage, Fresh Linen',
                'fragrance_strength': 'LIGHT',
                'size': 'MEDIUM',
                'burn_time': '40-50 hours',
                'mood': 'Calm, Clean, Zen',
                'recommended_rooms': 'Bathroom, Bedroom, Yoga Room',
                'recommended_occasions': 'Meditation, Self-care, Spa',
                'is_featured': True,
            },
        ]

        for product_data in products_data:
            product_data = dict(product_data)
            facet_values = {
                field: product_data.pop(field)
                for field in FACET_FIELDS
                if field in product_data
            }
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data,
            )
            if created:
                set_product_facets(product, facet_values)
                self.stdout.write(f'  Created product: {product.name}')

                # Set initial stock (Inventory auto-created by signal)
                inventory = Inventory.objects.get(product=product)
                inventory.quantity = 20
                inventory.reorder_level = 5
                inventory.save()

        # Update RAG knowledge for all products
        self.stdout.write('Generating knowledge documents and embeddings...')
        try:
            count = RAGService.update_all_products()
            self.stdout.write(self.style.SUCCESS(f'Updated knowledge for {count} products.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Knowledge update warning: {e}'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        if not admin_email or not admin_password:
            self.stdout.write('No seed admin was created. Use createsuperuser or set SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD.')
