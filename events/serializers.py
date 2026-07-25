from rest_framework import serializers
from .models import Event, EventImage
from vehicles.serializers import VehicleSerializer


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'uploaded_at']


class EventSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    images = EventImageSerializer(many=True, read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'vehicle', 'number_plate', 'description', 
            'event_type', 'event_type_display', 'image_link',
            'latitude', 'longitude', 'location', 'speed',
            'is_from_device', 'is_resolved', 'images', 'created_at'
        ]
        read_only_fields = ['created_at']


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events from the device"""
    class Meta:
        model = Event
        fields = [
            'number_plate', 'description', 'event_type',
            'image_link', 'latitude', 'longitude', 'location',
            'speed', 'is_from_device'
        ]


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.number_plate', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'number_plate', 'vehicle_plate', 'event_type',
            'event_type_display', 'image_link', 'latitude', 'longitude',
            'location', 'speed', 'is_resolved', 'created_at'
        ]
