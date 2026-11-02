from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.newsletter.models import NewsletterSubscription
from apps.storefront.models import SiteSettings

User = get_user_model()


def create_user(email, role=User.Role.CUSTOMER):
    return User.objects.create_user(
        email=email, username=email.split('@')[0], first_name='Tester',
        password='Candle-River-928!Silver', role=role,
    )


class NewsletterAndSettingsApiTests(APITestCase):
    def setUp(self):
        self.customer = create_user('buyer@example.com')
        self.admin = create_user('admin@example.com', User.Role.ADMIN)

    def test_newsletter_subscribe_reactivate_and_admin_management(self):
        first = self.client.post('/api/newsletter/subscribe/', {'email': ' Reader@Example.com '}, format='json')
        self.assertEqual(first.status_code, 201, first.data)
        subscription = NewsletterSubscription.objects.get(email='reader@example.com')
        duplicate = self.client.post('/api/newsletter/subscribe/', {'email': 'reader@example.com'}, format='json')
        self.assertEqual(duplicate.status_code, 400)

        self.client.force_authenticate(user=self.customer)
        denied = self.client.get('/api/newsletter/admin/')
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(user=self.admin)
        listing = self.client.get('/api/newsletter/admin/')
        self.assertEqual(listing.status_code, 200, listing.data)
        stats = self.client.get('/api/newsletter/admin/stats/')
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.data['data']['total'], 1)
        changed = self.client.patch(f'/api/newsletter/admin/{subscription.id}/', {'is_active': False}, format='json')
        self.assertEqual(changed.status_code, 200, changed.data)
        self.assertFalse(changed.data['data']['is_active'])

        subscription.refresh_from_db()
        reactivated = self.client.post('/api/newsletter/subscribe/', {'email': subscription.email}, format='json')
        self.assertEqual(reactivated.status_code, 201, reactivated.data)
        unsubscribed = self.client.post('/api/newsletter/unsubscribe/', {'token': str(subscription.unsubscribe_token)}, format='json')
        self.assertEqual(unsubscribed.status_code, 200)

    def test_store_settings_are_public_read_and_admin_write(self):
        public = self.client.get('/api/settings/')
        self.assertEqual(public.status_code, 200, public.data)
        self.assertTrue(SiteSettings.objects.filter(pk=1).exists())

        payload = {'site_name': 'Test Candles'}
        self.client.force_authenticate(user=self.customer)
        denied = self.client.patch('/api/settings/', payload, format='json')
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(user=self.admin)
        saved = self.client.patch('/api/settings/', payload, format='json')
        self.assertEqual(saved.status_code, 200, saved.data)
        self.assertEqual(SiteSettings.objects.get(pk=1).site_name, 'Test Candles')
