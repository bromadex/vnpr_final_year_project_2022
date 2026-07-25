from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Event, EventImage
from .serializers import EventSerializer, EventCreateSerializer, EventListSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventListSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['number_plate', 'description', 'location']

    def get_queryset(self):
        queryset = Event.objects.all()
        event_type = self.request.query_params.get('type', None)
        is_resolved = self.request.query_params.get('resolved', None)

        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')

        return queryset


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event = serializer.save()
        images = self.request.FILES.getlist('images')
        for image in images:
            EventImage.objects.create(event=event, image=image)

        # Broadcast via WebSocket
        self.broadcast_event(event)
        return event

    def broadcast_event(self, event):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "incidents",
            {
                "type": "incident_message",
                "message": {
                    "id": event.id,
                    "number_plate": event.number_plate,
                    "event_type": event.event_type,
                    "location": event.location,
                    "created_at": event.created_at.isoformat(),
                    "image_link": event.image_link,
                    "latitude": str(event.latitude) if event.latitude else None,
                    "longitude": str(event.longitude) if event.longitude else None,
                }
            }
        )


class EventUpdateView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'


class EventDeleteView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'


class HomePageView(generics.GenericAPIView):
    """Simple home page view"""
    def get(self, request):
        return Response({"message": "Welcome to VNPR API", "status": "online"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_event(request, pk):
    """Mark an event as resolved (fine paid)"""
    event = get_object_or_404(Event, pk=pk)
    event.is_resolved = True
    event.save()
    return Response({"status": "resolved", "event_id": event.id})


@api_view(['POST'])
def device_event(request):
    """Endpoint for Raspberry Pi to push events"""
    # This endpoint can have API key auth instead of session auth
    serializer = EventCreateSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save()

        # Try to match with vehicle database
        try:
            from vehicles.models import Vehicle
            vehicle = Vehicle.objects.get(number_plate__iexact=event.number_plate)
            event.vehicle = vehicle
            event.save()
        except Vehicle.DoesNotExist:
            pass

        # Broadcast via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "incidents",
            {
                "type": "incident_message",
                "message": {
                    "id": event.id,
                    "number_plate": event.number_plate,
                    "event_type": event.event_type,
                    "location": event.location,
                    "created_at": event.created_at.isoformat(),
                    "image_link": event.image_link,
                    "latitude": str(event.latitude) if event.latitude else None,
                    "longitude": str(event.longitude) if event.longitude else None,
                }
            }
        )

        return Response({"status": "success", "event_id": event.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
