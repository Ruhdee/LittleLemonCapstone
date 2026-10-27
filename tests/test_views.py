from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from restaurant.models import Booking, Menu
from restaurant.serializers import MenuSerializer


class MenuViewTest(APITestCase):
    def setUp(self):
        Menu.objects.create(name='Greek Salad', price=12, menu_item_description='Crisp lettuce and feta')
        Menu.objects.create(name='Bruschetta', price=8, menu_item_description='Grilled bread with tomato')
        Menu.objects.create(name='Lemon Dessert', price=7, menu_item_description='Classic lemon cake')
        self.staff = User.objects.create_user(username='manager', password='Str0ng-pass-123', is_staff=True)
        self.customer = User.objects.create_user(username='guest', password='Str0ng-pass-123')

    def test_get_all(self):
        response = self.client.get('/api/menu-items/')
        expected = MenuSerializer(Menu.objects.all().order_by('id'), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def test_get_single_item(self):
        item = Menu.objects.get(name='Bruschetta')
        response = self.client.get(f'/api/menu-items/{item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Bruschetta')

    def test_missing_item_returns_404(self):
        response = self.client.get('/api/menu-items/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_cannot_create_item(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post('/api/menu-items/', {'name': 'Pasta', 'price': 15}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Menu.objects.filter(name='Pasta').exists())

    def test_staff_can_create_item(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post('/api/menu-items/', {'name': 'Pasta', 'price': 15}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Menu.objects.filter(name='Pasta').exists())

    def test_negative_price_is_rejected(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post('/api/menu-items/', {'name': 'Free Food', 'price': -1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookingViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='guest', password='Str0ng-pass-123')
        Booking.objects.create(first_name='Ana', reservation_date='2026-12-01', reservation_slot=18)

    def test_requires_authentication(self):
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_booking(self):
        self.client.force_authenticate(self.user)
        data = {'first_name': 'Ben', 'reservation_date': '2026-12-01', 'reservation_slot': 19}
        response = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)

    def test_double_booking_is_rejected(self):
        self.client.force_authenticate(self.user)
        data = {'first_name': 'Ben', 'reservation_date': '2026-12-01', 'reservation_slot': 18}
        response = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)

    def test_slot_outside_opening_hours_is_rejected(self):
        self.client.force_authenticate(self.user)
        data = {'first_name': 'Ben', 'reservation_date': '2026-12-01', 'reservation_slot': 23}
        response = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_date(self):
        Booking.objects.create(first_name='Cara', reservation_date='2026-12-02', reservation_slot=12)
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/bookings/?date=2026-12-02')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([booking['first_name'] for booking in response.data], ['Cara'])

    def test_update_and_delete_booking(self):
        booking = Booking.objects.get(first_name='Ana')
        self.client.force_authenticate(self.user)
        response = self.client.patch(f'/api/bookings/{booking.id}/', {'reservation_slot': 12}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reservation_slot'], 12)
        response = self.client.delete(f'/api/bookings/{booking.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.exists())


class AuthenticationTest(APITestCase):
    def test_register_and_get_token(self):
        data = {'username': 'newguest', 'email': 'newguest@example.com', 'password': 'Str0ng-pass-123'}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/token/login/', {'username': 'newguest', 'password': 'Str0ng-pass-123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['auth_token']
        self.assertTrue(Token.objects.filter(key=token, user__username='newguest').exists())

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password_gets_no_token(self):
        User.objects.create_user(username='guest', password='Str0ng-pass-123')
        response = self.client.post('/api/token/login/', {'username': 'guest', 'password': 'wrong-password'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('auth_token', response.data)


class PageViewTest(APITestCase):
    def test_pages_are_served(self):
        for url in ['/', '/about/', '/menu/', '/book/', '/reservations/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
