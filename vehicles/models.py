from django.db import models


def upload_gallery_image(instance, filename):
    return f"images/vehicles/{instance.vehicle.number_plate}/{instance.vehicle.id}/gallery/{filename}"


class Vehicle(models.Model):
    vehicle_name = models.CharField(max_length=30, null=False, blank=False)
    number_plate = models.CharField(max_length=10, null=False, blank=False, unique=True)
    vehicle_owner = models.CharField(max_length=50, null=False, blank=False)
    vehicle_model = models.CharField(max_length=30, null=False, blank=False)
    year = models.CharField(max_length=5, null=False, blank=False)
    vehicle_owner_address = models.CharField(max_length=70, null=False, blank=False)
    vehicle_owner_phone = models.CharField(max_length=13, null=False, blank=False)
    image_delete = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number_plate} - {self.vehicle_name}"


class VehicleImage(models.Model):
    image = models.FileField(upload_to=upload_gallery_image, null=False, blank=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.vehicle.number_plate}"
