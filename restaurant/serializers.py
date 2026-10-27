from rest_framework import serializers

from .models import Booking, Menu


class MenuSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(min_value=0)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'price', 'menu_item_description']


class BookingSerializer(serializers.ModelSerializer):
    reservation_slot = serializers.IntegerField(min_value=10, max_value=19)

    class Meta:
        model = Booking
        fields = ['id', 'first_name', 'reservation_date', 'reservation_slot']

    def validate(self, attrs):
        reservation_date = attrs.get('reservation_date', getattr(self.instance, 'reservation_date', None))
        reservation_slot = attrs.get('reservation_slot', getattr(self.instance, 'reservation_slot', None))
        clashes = Booking.objects.filter(reservation_date=reservation_date, reservation_slot=reservation_slot)
        if self.instance is not None:
            clashes = clashes.exclude(pk=self.instance.pk)
        if clashes.exists():
            raise serializers.ValidationError('This time slot is already booked for that date.')
        return attrs
