from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationFlowTests(APITestCase):
    def test_registration_hashes_password_and_never_accepts_admin_role(self):
        response = self.client.post('/api/auth/register/', {
            'email': 'New.User@example.com',
            'username': 'new-user',
            'first_name': 'New User',
            'password': 'Candle-River-928!Silver',
            'password_confirm': 'Candle-River-928!Silver',
            'role': 'ADMIN',
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        user = User.objects.get(email='new.user@example.com')
        self.assertTrue(user.check_password('Candle-River-928!Silver'))
        self.assertNotEqual(user.password, 'Candle-River-928!Silver')
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertIn('access', response.data['data'])
        self.assertNotIn('refresh', response.data['data'])
        cookie = response.cookies['wax_refresh']
        self.assertTrue(cookie['httponly'])
        self.assertIn('no-store', response['Cache-Control'])

    def test_registration_rejects_mismatched_or_weak_password(self):
        payload = {
            'email': 'new@example.com', 'username': 'new-user', 'first_name': 'New',
            'password': 'password', 'password_confirm': 'different',
        }
        response = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email='new@example.com').exists())

    def test_login_refresh_rotation_and_logout_revoke_refresh_cookie(self):
        user = User.objects.create_user(
            email='buyer@example.com', username='buyer', first_name='Buyer',
            password='Candle-River-928!Silver',
        )
        login = self.client.post('/api/auth/login/', {
            'email': 'BUYER@EXAMPLE.COM', 'password': 'Candle-River-928!Silver',
        }, format='json')
        self.assertEqual(login.status_code, 200, login.data)
        old_refresh = self.client.cookies['wax_refresh'].value
        self.assertIn('access', login.data['data'])
        self.assertNotIn('refresh', login.data['data'])

        refreshed = self.client.post('/api/auth/token/refresh/', {}, format='json')
        self.assertEqual(refreshed.status_code, 200, refreshed.data)
        self.assertNotEqual(self.client.cookies['wax_refresh'].value, old_refresh)
        access = refreshed.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        profile = self.client.get('/api/auth/profile/')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data['data']['email'], user.email)
        self.assertFalse(profile.data['data']['is_admin'])

        logout = self.client.post('/api/auth/logout/', {}, format='json')
        self.assertEqual(logout.status_code, 200, logout.data)
        self.assertEqual(self.client.cookies['wax_refresh'].value, '')
        self.client.credentials()
        rejected = self.client.post('/api/auth/token/refresh/', {}, format='json')
        self.assertEqual(rejected.status_code, 401)

    def test_profile_rejects_bad_postal_code_and_ignores_role_escalation(self):
        user = User.objects.create_user(
            email='buyer@example.com', username='buyer', first_name='Buyer',
            password='Candle-River-928!Silver',
        )
        self.client.force_authenticate(user=user)
        bad = self.client.patch('/api/auth/profile/', {'pincode': '12AB'}, format='json')
        self.assertEqual(bad.status_code, 400)
        escalated = self.client.patch('/api/auth/profile/', {'role': 'ADMIN'}, format='json')
        self.assertEqual(escalated.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_auth_endpoints_reject_untrusted_browser_origins(self):
        response = self.client.post(
            '/api/auth/login/', {'email': 'x@example.com', 'password': 'irrelevant'},
            format='json', HTTP_ORIGIN='https://attacker.example',
        )
        self.assertEqual(response.status_code, 403)


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com', username='admin', first_name='Admin',
            password='Candle-River-928!Silver', role=User.Role.ADMIN,
        )
        self.customer = User.objects.create_user(
            email='customer@example.com', username='customer', first_name='Customer',
            password='Candle-River-928!Silver',
        )

    def test_user_directory_is_admin_only_and_excludes_credentials(self):
        self.client.force_authenticate(user=self.customer)
        denied = self.client.get('/api/users/')
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/?search=customer')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['results'][0]['email'], self.customer.email)
        self.assertNotIn('password', response.data['results'][0])

    def test_admin_can_suspend_restore_customer_but_not_self(self):
        self.client.force_authenticate(user=self.admin)
        suspended = self.client.patch(f'/api/users/{self.customer.id}/', {'is_active': False}, format='json')
        self.assertEqual(suspended.status_code, 200, suspended.data)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)

        restored = self.client.patch(f'/api/users/{self.customer.id}/', {'is_active': True}, format='json')
        self.assertEqual(restored.status_code, 200, restored.data)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_active)

        own_account = self.client.patch(f'/api/users/{self.admin.id}/', {'is_active': False}, format='json')
        self.assertEqual(own_account.status_code, 400)
