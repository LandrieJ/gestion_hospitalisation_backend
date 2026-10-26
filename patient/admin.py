from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'genre', 'age_connu', 'age',
        'cin_connu', 'cin_number', 'etat_de_la_personne', 'date_registered', 'registered_by'
    )
    list_filter = ('genre', 'age_connu', 'cin_connu', 'date_registered')
    search_fields = ('first_name', 'last_name', 'cin_number')
    ordering = ('-date_registered',)
    
    readonly_fields = ('date_registered', 'registered_by')
    exclude = ('hospitals',)  # Masquer dans le formulaire admin

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # si c'est un nouveau patient
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)
        
        # Associer automatiquement l'hôpital
        if hasattr(request.user, 'hospital') and request.user.hospital:
            obj.hospitals.set([request.user.hospital])
