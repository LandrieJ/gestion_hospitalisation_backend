from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .models import Evenement
from .serializers import EvenementSerializer

class EvenementViewSet(viewsets.ModelViewSet):
    queryset = Evenement.objects.all().order_by("time")
    serializer_class = EvenementSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['event', 'type', 'service']
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)