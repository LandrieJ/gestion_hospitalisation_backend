from django.contrib import admin
from .models import Hospital

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "address", "phone_number")
    search_fields = ("name", "code", "address", "phone_number")
    list_filter = ("name",)
