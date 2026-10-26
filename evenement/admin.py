from django.contrib import admin
from .models import Evenement

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('event', 'type', 'service', 'owner', 'time')
    search_fields = ('event', 'type', 'service')
