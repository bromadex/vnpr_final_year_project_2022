from django.urls import path
from .views import (
    EventListView, EventDetailView, EventCreateView,
    EventUpdateView, EventDeleteView, HomePageView,
    resolve_event, device_event
)

app_name = 'events'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('list/', EventListView.as_view(), name='list'),
    path('new/', EventCreateView.as_view(), name='add_event'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/edit/', EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('<int:pk>/resolve/', resolve_event, name='resolve_event'),
    path('device/', device_event, name='device_event'),
]
