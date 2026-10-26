from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comptes/', include('comptes.urls')),
    path('hospitals/', include('hospital.urls')),
    path('services/', include('service.urls')),
    path('patient/', include('patient.urls')),
    path('traumatologie/', include('traumatologie.urls')),
    path('logistique/', include('logistique.urls')),
    path('evenement/', include('evenement.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)