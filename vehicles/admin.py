from django.contrib import admin
from .models import Vehicle, VehicleImage


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['number_plate', 'vehicle_name', 'vehicle_owner', 'year', 'created_at']
    list_filter = ['year', 'created_at']
    search_fields = ['number_plate', 'vehicle_name', 'vehicle_owner']
    inlines = [VehicleImageInline]


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'uploaded_at']
