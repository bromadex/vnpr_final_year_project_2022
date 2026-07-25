from django.contrib import admin
from .models import Event, EventImage


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['number_plate', 'event_type', 'location', 'speed', 'is_resolved', 'created_at']
    list_filter = ['event_type', 'is_resolved', 'is_from_device', 'created_at']
    search_fields = ['number_plate', 'description', 'location']
    inlines = [EventImageInline]


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ['event', 'uploaded_at']
