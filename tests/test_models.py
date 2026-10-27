from datetime import date

from django.test import TestCase

from restaurant.models import Booking, Menu


class MenuModelTest(TestCase):
    def test_string_is_name(self):
        item = Menu.objects.create(name='Greek Salad', price=12, menu_item_description='Crisp lettuce and feta')
        self.assertEqual(str(item), 'Greek Salad')

    def test_description_defaults_to_empty(self):
        item = Menu.objects.create(name='Bruschetta', price=8)
        self.assertEqual(item.menu_item_description, '')


class BookingModelTest(TestCase):
    def test_string_is_first_name(self):
        booking = Booking.objects.create(first_name='Ana', reservation_date=date(2026, 12, 1), reservation_slot=18)
        self.assertEqual(str(booking), 'Ana')

    def test_slot_defaults_to_ten(self):
        booking = Booking.objects.create(first_name='Ben', reservation_date=date(2026, 12, 1))
        self.assertEqual(booking.reservation_slot, 10)
