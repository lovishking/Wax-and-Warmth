from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework.test import APITestCase

from apps.products.models import Category, Product

User = get_user_model()


def user_with_role(email, role):
    return User.objects.create_user(
        email=email, username=email.split('@')[0], first_name='Tester',
        password='Candle-River-928!Silver', role=role,
    )


class ProductApiTests(APITestCase):
    def setUp(self):
        self.customer = user_with_role('buyer@example.com', User.Role.CUSTOMER)
        self.admin = user_with_role('admin@example.com', User.Role.ADMIN)
        self.category = Category.objects.create(name='Candles')

    def product(self, **overrides):
        values = {
            'name': 'Rose Candle', 'description': 'A soft floral candle', 'price': '12.50',
            'category': self.category, 'image': 'products/smallbubble.jpg',
            'is_active': True, 'is_featured': True,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    def test_public_product_list_and_product_image_url_load(self):
        product = self.product()
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'][0]['id'], product.id)
        self.assertEqual(response.data['results'][0]['scent_notes_list'], [])
        image_url = response.data['results'][0]['image']
        self.assertIn('/media/products/smallbubble.jpg', image_url)
        with override_settings(DEBUG=True):
            image_response = self.client.get('/media/products/smallbubble.jpg')
        self.assertEqual(image_response.status_code, 200)
        self.assertEqual(image_response['Content-Type'], 'image/jpeg')
        image_response.close()

    def test_featured_products_are_public_for_homepage(self):
        product = self.product()
        response = self.client.get('/api/products/featured/')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['data'][0]['id'], product.id)
        self.assertEqual(response.data['data'][0]['stock_status'], 'OUT_OF_STOCK')

    def test_product_create_requires_admin_and_valid_price(self):
        payload = {
            'name': 'New Candle', 'description': 'A handmade candle', 'price': '15.00',
            'category': self.category.id, 'scent_family': 'FLORAL', 'scent_notes': 'Rose',
        }
        self.client.force_authenticate(user=self.customer)
        denied = self.client.post('/api/products/', payload, format='json')
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(user=self.admin)
        invalid = self.client.post('/api/products/', {**payload, 'price': '0'}, format='json')
        self.assertEqual(invalid.status_code, 400)
        created = self.client.post('/api/products/', payload, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        self.assertTrue(Product.objects.filter(name='New Candle').exists())

    def test_uploaded_image_is_saved_and_served(self):
        buffer = BytesIO()
        Image.new('RGB', (3, 3), color='burlywood').save(buffer, format='PNG')
        upload = SimpleUploadedFile('new-candle.png', buffer.getvalue(), content_type='image/png')
        payload = {
            'name': 'Uploaded Candle', 'description': 'Image upload', 'price': '22.00',
            'category': str(self.category.id), 'scent_family': 'FLORAL', 'scent_notes': 'Rose',
            'image': upload,
        }
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root, DEBUG=True):
            self.client.force_authenticate(user=self.admin)
            response = self.client.post('/api/products/', payload, format='multipart')
            self.assertEqual(response.status_code, 201, response.data)
            image_path = response.data['image'].split('/media/', 1)[1]
            fetched = self.client.get(f'/media/{image_path}')
            self.assertEqual(fetched.status_code, 200)
            self.assertEqual(fetched['Content-Type'], 'image/png')
            fetched.close()

    def test_category_public_read_admin_write(self):
        response = self.client.get('/api/products/categories/')
        self.assertEqual(response.status_code, 200)
        self.client.force_authenticate(user=self.customer)
        denied = self.client.post('/api/products/categories/', {'name': 'Latte'}, format='json')
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(user=self.admin)
        created = self.client.post('/api/products/categories/', {'name': 'Latte'}, format='json')
        self.assertEqual(created.status_code, 201, created.data)

    def test_delete_archives_catalog_product(self):
        product = self.product()
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 204)
        product.refresh_from_db()
        self.assertFalse(product.is_active)
