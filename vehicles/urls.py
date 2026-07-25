from django.urls import path
from .views import (
    VehicleListView, VehicleDetailView, VehicleCreateView,
    VehicleUpdateView, VehicleDeleteView, VehicleSearchView
)

app_name = 'vehicles'

urlpatterns = [
    path('', VehicleListView.as_view(), name='list'),
    path('search/', VehicleSearchView.as_view(), name='search'),
    path('new/', VehicleCreateView.as_view(), name='add_vehicle'),
    path('<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('<int:pk>/edit/', VehicleUpdateView.as_view(), name='vehicle_update'),
    path('<int:pk>/delete/', VehicleDeleteView.as_view(), name='vehicle_delete'),
]
