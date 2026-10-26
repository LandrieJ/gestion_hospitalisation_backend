from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser,
    Education,
    Certification,
    Specialite,
    Horaire,
    Competence,
    Statistique,
    Blocage,
)


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


class SpecialiteInline(admin.TabularInline):
    model = Specialite
    extra = 0


class HoraireInline(admin.StackedInline):
    model = Horaire
    extra = 0
    max_num = 1


class CompetenceInline(admin.TabularInline):
    model = Competence
    extra = 0


class StatistiqueInline(admin.StackedInline):
    model = Statistique
    extra = 0
    max_num = 1


class BlocageInline(admin.TabularInline):
    model = Blocage
    extra = 0


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {
            'fields': (
                'first_name', 'last_name', 'profile_picture', 'phone_number',
                'address', 'biographie', 'hospital','service', 'user_type', 'status'
            )
        }),
        ('Professionnel', {
            'fields': (
                'fonction', 'matricule_professionnel',
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'password1', 'password2',
                'user_type', 'hospital'
            ),
        }),
    )

    list_display = ('email', 'first_name', 'last_name', 'user_type', 'hospital', 'is_active')
    list_filter = ('user_type', 'hospital', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('user_permissions',)

    inlines = [
        EducationInline,
        CertificationInline,
        SpecialiteInline,
        HoraireInline,
        CompetenceInline,
        StatistiqueInline,
        BlocageInline,
    ]


# Autres modèles (si tu veux les voir aussi dans l'admin séparément)
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user', 'diplome', 'etablissement', 'annee')
    search_fields = ('diplome', 'etablissement', 'user__email')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'certification')


@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialite')


@admin.register(Horaire)
class HoraireAdmin(admin.ModelAdmin):
    list_display = ('user', 'debut', 'fin')


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'nom', 'niveau')


@admin.register(Statistique)
class StatistiqueAdmin(admin.ModelAdmin):
    list_display = ('user', 'patients', 'experience', 'consultations')


@admin.register(Blocage)
class BlocageAdmin(admin.ModelAdmin):
    list_display = ('user', 'raison', 'date', 'par')
    search_fields = ('raison', 'par', 'user__email')