from django.db import models
from vehicles.models import Vehicle


def upload_event_image(instance, filename):
    return f"images/events/{instance.event.id}/gallery/{filename}"


class Event(models.Model):
    RED_ROBOT = 'RED_ROBOT'
    OVER_SPEEDING = 'OVER_SPEEDING'
    INFRACTIONS = [
        (RED_ROBOT, 'Crossed Red Light'),
        (OVER_SPEEDING, 'Over Speeding'),
    ]

    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.SET_NULL, 
        related_name='events',
        null=True, 
        blank=True
    )
    number_plate = models.CharField(max_length=10, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    event_type = models.CharField(
        max_length=13, 
        null=False, 
        blank=False, 
        choices=INFRACTIONS, 
        default=OVER_SPEEDING
    )
    image_link = models.URLField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)  # km/h
    is_from_device = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number_plate} - {self.event_type} at {self.created_at}"


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to=upload_event_image, null=False, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Event {self.event.id}"
