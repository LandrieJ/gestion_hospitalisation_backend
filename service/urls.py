# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, BedViewSet

# Router principal
router = DefaultRouter()
router.register(r'lists', ServiceViewSet, basename='service')
router.register(r'beds', BedViewSet, basename='bed')

urlpatterns = [
    path('', include(router.urls)),
]
