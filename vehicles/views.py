from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Vehicle, VehicleImage
from .serializers import VehicleSerializer, VehicleListSerializer, VehicleImageSerializer


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class VehicleListView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['number_plate', 'vehicle_name', 'vehicle_owner']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class VehicleDetailView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'


class VehicleCreateView(generics.CreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        vehicle = serializer.save()
        images = self.request.FILES.getlist('images')
        for image in images:
            VehicleImage.objects.create(vehicle=vehicle, image=image)
        return vehicle


class VehicleUpdateView(generics.UpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        vehicle = serializer.save()
        images_delete = self.request.POST.getlist('image_delete')
        if images_delete:
            VehicleImage.objects.filter(id__in=images_delete).delete()
        images = self.request.FILES.getlist('images')
        for image in images:
            VehicleImage.objects.create(vehicle=vehicle, image=image)
        return vehicle


class VehicleDeleteView(generics.DestroyAPIView):
    queryset = Vehicle.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        # Delete associated images from storage
        for img in instance.images.all():
            img.image.delete(save=False)
        instance.delete()


class VehicleSearchView(generics.ListAPIView):
    serializer_class = VehicleListSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Vehicle.objects.filter(
                Q(number_plate__icontains=query) |
                Q(vehicle_name__icontains=query) |
                Q(vehicle_owner__icontains=query)
            ).distinct()
        return Vehicle.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
