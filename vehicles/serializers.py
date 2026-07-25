from rest_framework import serializers
from .models import Vehicle, VehicleImage


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'uploaded_at']


class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_name', 'number_plate', 'vehicle_owner',
            'vehicle_model', 'year', 'vehicle_owner_address', 
            'vehicle_owner_phone', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VehicleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    first_image = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_name', 'number_plate', 'vehicle_owner', 
                  'vehicle_model', 'first_image']

    def get_first_image(self, obj):
        first = obj.images.first()
        if first:
            return self.context['request'].build_absolute_uri(first.image.url)
        return None
