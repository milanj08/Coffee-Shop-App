"""Tests for authentication and authorization.

These go through HTTP with APIClient rather than calling functions directly,
because permission classes only run inside the request cycle. That is the
opposite trade-off from test_sale in tests.py, and deliberately so: business
rules are tested without a server, access rules are tested with one.

The test worth reading first is
`test_barista_cannot_reach_a_manager_endpoint`. Most people stop at
"logged in vs logged out" and never check *which* role - and that is the
difference between authentication and authorization.
"""

from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Accounting, Barista, Employee, InventoryManagement, Manager, Menu, Recipe


class AuthTestBase(APITestCase):
    def setUp(self):
        self.manager_user = User.objects.create_user(
            username='the_manager', password='CoffeeShop2026'
        )
        manager_employee = Employee.objects.create(
            ssn=Decimal('111111111'), first_name='Meg', last_name='Manager',
            email='meg@example.com', salary=Decimal('60000.00'),
            user=self.manager_user,
        )
        Manager.objects.create(ssn=manager_employee, percentage_ownership=Decimal('10.00'))

        self.barista_user = User.objects.create_user(
            username='the_barista', password='CoffeeShop2026'
        )
        barista_employee = Employee.objects.create(
            ssn=Decimal('222222222'), first_name='Baz', last_name='Barista',
            email='baz@example.com', salary=Decimal('30000.00'),
            user=self.barista_user,
        )
        Barista.objects.create(
            ssn=barista_employee, day='2026-08-06',
            start_time='09:00:00', end_time='17:00:00',
        )

    def login(self, username):
        response = self.client.post(
            '/api/auth/login/',
            {'username': username, 'password': 'CoffeeShop2026'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        return response.data


class LoginTests(AuthTestBase):
    def test_login_returns_a_token_and_the_role_from_the_database(self):
        data = self.login('the_manager')

        self.assertIn('token', data)
        self.assertEqual(data['role'], 'manager')
        # The role is never sent by the client and never stored on the User.
        self.assertEqual(data['username'], 'the_manager')

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'the_manager', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_is_never_stored_in_plain_text(self):
        """The original app kept a username->password map in localStorage."""
        stored = User.objects.get(username='the_barista').password

        self.assertNotEqual(stored, 'CoffeeShop2026')
        self.assertTrue(stored.startswith('pbkdf2_'))

    def test_logout_invalidates_the_token(self):
        self.login('the_barista')

        self.client.post('/api/auth/logout/')

        # Same token, now worthless. Clearing localStorage alone would have
        # left this working.
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(AuthTestBase):
    def test_anonymous_requests_are_rejected(self):
        """Every one of these used to return 200 with the full table."""
        for url in ['/api/inventory/', '/api/menu/', '/api/baristas/', '/api/accounting/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_barista_cannot_reach_a_manager_endpoint(self):
        """The test that matters.

        Authentication is "who are you". This is "what may you do". A valid
        token is not enough - the role is checked on every request.
        """
        self.login('the_barista')

        response = self.client.get('/api/baristas/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_reach_a_manager_endpoint(self):
        self.login('the_manager')

        response = self.client.get('/api/baristas/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_barista_can_read_the_menu_but_not_change_it(self):
        self.login('the_barista')

        self.assertEqual(self.client.get('/api/menu/').status_code, status.HTTP_200_OK)

        response = self.client.post('/api/menu/', {
            'name': 'Free Coffee', 'size': '350.00', 'type': 'coffee',
            'price': '0.00', 'hot_cold': 'hot',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Menu.objects.filter(name='Free Coffee').exists())

    def test_barista_can_record_a_sale(self):
        milk = InventoryManagement.objects.create(
            name='Milk', unit='ml', quantity=Decimal('1000'), price=Decimal('3.50')
        )
        latte = Menu.objects.create(
            name='Latte', size=350, type='coffee', price=Decimal('4.50'), hot_cold='hot'
        )
        Recipe.objects.create(
            recipe_name=latte, ingredient_name=milk,
            ingredient_quantity=Decimal('300'), ingredient_unit='ml',
            position_number=1, execution_description='Steam the milk.',
        )
        Accounting.objects.create(
            day='2026-08-06', time='09:00:00', account_balance=Decimal('100.00')
        )
        self.login('the_barista')

        response = self.client.post('/api/sales/record-sale', {
            'items': [{'drink_name': 'Latte', 'quantity': 1}],
            'payment_method': 'cash',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)


class RegistrationTests(AuthTestBase):
    def payload(self, **overrides):
        data = {
            'username': 'newhire',
            'password': 'CoffeeShop2026',
            'first_name': 'New',
            'last_name': 'Hire',
            'email': 'new@example.com',
        }
        data.update(overrides)
        return data

    def test_signup_creates_a_barista(self):
        response = self.client.post('/api/auth/register/', self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['role'], 'barista')
        self.assertIn('token', response.data)

    def test_signup_cannot_grant_manager(self):
        """The original bug: naming yourself manager_anything made you one.

        There is no role field on the serializer, so an attempt to supply one
        is ignored rather than honoured.
        """
        response = self.client.post(
            '/api/auth/register/',
            self.payload(username='manager_lol', role='manager'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'barista')

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        self.assertEqual(
            self.client.get('/api/baristas/').status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_duplicate_username_is_rejected(self):
        response = self.client.post(
            '/api/auth/register/', self.payload(username='the_barista'), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_weak_password_is_rejected(self):
        """AUTH_PASSWORD_VALIDATORS has been in settings.py, unused, since the
        project was generated."""
        response = self.client.post(
            '/api/auth/register/', self.payload(password='abc'), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_a_failed_signup_leaves_nothing_behind(self):
        before = Employee.objects.count()

        self.client.post(
            '/api/auth/register/', self.payload(password='abc'), format='json'
        )

        self.assertEqual(Employee.objects.count(), before)
        self.assertFalse(User.objects.filter(username='newhire').exists())
