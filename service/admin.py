from django.contrib import admin
from .models import Service, Bed

class BedInline(admin.TabularInline):
    model = Bed
    extra = 0
    readonly_fields = ("code", "is_occupied")
    can_delete = True

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "hospital", "nombre_chambre", "nombre_lits_par_chambre")
    list_filter = ("hospital", "name")
    search_fields = ("name", "code", "hospital__name")
    inlines = [BedInline]
    readonly_fields = ("code",)

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("code", "service", "is_occupied")
    list_filter = ("service__hospital", "is_occupied")
    search_fields = ("code", "service__name")
