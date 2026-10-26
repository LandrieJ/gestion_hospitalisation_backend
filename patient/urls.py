from django.urls import path
from .views import PatientAPIView, PatientDetailAPIView

urlpatterns = [
    path('', PatientAPIView.as_view(), name='patient_add'),
    path('<int:pk>/', PatientDetailAPIView.as_view(), name='patient_detail'),
]