from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import timedelta

from .models import (
    # Modèles de référence
    ProcedureType,
    DiagnosticTestType,
    MedicamentType,
    LocalisationType,
    ConditionType,
    Geolocalisation,
    # Modèle central
    DossierMedical,
    AutorisationAccesDossier,
    # Sections du dossier
    InformationVariantPatient,
    SignesVitaux,
    EvaluationABCDE,
    Triage,
    HistoriqueMedical,
    HistoriqueMaladieActuelle,
    Blessures,
    BlessureDetail,
    InterventionsUrgencesMedicamentsLiquide,
    InterventionsUrgencesProcedures,
    InterventionsUrgencesTestsDiagnostiques,
    DispositionUniteUrgence,
)


# ==================== FILTRES PERSONNALISÉS ====================


class StatutDossierFilter(SimpleListFilter):
    title = "Statut du dossier"
    parameter_name = "statut_filtre"

    def lookups(self, request, model_admin):
        return (
            ("actifs", "Dossiers actifs (Ouverts + En cours)"),
            ("fermes_recents", "Fermés dans les 7 derniers jours"),
            ("archives", "Archivés"),
        )

    def queryset(self, request, queryset):
        if self.value() == "actifs":
            return queryset.filter(statut__in=["ouvert", "en_cours"])
        elif self.value() == "fermes_recents":
            date_limite = timezone.now() - timedelta(days=7)
            return queryset.filter(statut="ferme", date_modification__gte=date_limite)
        elif self.value() == "archives":
            return queryset.filter(statut="archive")
        return queryset


class HopitalFilter(SimpleListFilter):
    title = "Hôpital"
    parameter_name = "hospital"

    def lookups(self, request, model_admin):
        from comptes.models import Hospital

        hospitals = Hospital.objects.all()
        return [(h.id, h.name) for h in hospitals]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(hospital__id=self.value())
        return queryset


# ==================== INLINES ====================


class AutorisationAccesDossierInline(admin.TabularInline):
    model = AutorisationAccesDossier
    fk_name = "dossier"
    extra = 0
    readonly_fields = ["date_demande", "date_reponse"]
    fields = [
        "hospital_demandeur",
        "statut",
        "motif_demande",
        "date_demande",
        "approbateur",
        "date_reponse",
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "hospital_demandeur",
                "hospital_proprietaire",
                "demandeur",
                "approbateur",
            )
        )


class BlessureDetailInline(admin.TabularInline):
    model = BlessureDetail
    extra = 1
    filter_horizontal = ["conditions"]


class SectionsInlineMixin:
    """Mixin pour les inlines de sections du dossier."""

    extra = 0
    max_num = 1
    readonly_fields = ["date_creation", "date_modification"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("enregistre_par")
            .filter(enregistre_par__isnull=False)
        )


class InformationVariantPatientInline(SectionsInlineMixin, admin.StackedInline):
    model = InformationVariantPatient
    fieldsets = (
        (
            "Arrivée",
            {"fields": (("mode_arrivee", "autre_mode_arrivee"), "accident_de_masse")},
        ),
        (
            "Profession",
            {"fields": (("classification_profession", "profession_specifique"),)},
        ),
        (
            "Localisation",
            {
                "fields": (
                    ("domicile", "residence_secondaire"),
                    ("lieu_accident", "geolocalisation"),
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


class SignesVitauxInline(SectionsInlineMixin, admin.StackedInline):
    model = SignesVitaux
    fieldsets = (
        ("État général", {"fields": ("signes_de_vie",)}),
        (
            "Mesures vitales",
            {
                "fields": (
                    (
                        "pression_arterielle_systolique",
                        "pression_arterielle_diastolique",
                    ),
                    ("frequence_cardiaque", "frequence_respiratoire"),
                    ("saturation_oxygene", "administration_oxygene"),
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


class EvaluationABCDEInline(SectionsInlineMixin, admin.StackedInline):
    model = EvaluationABCDE
    readonly_fields = SectionsInlineMixin.readonly_fields + ["score_glasgow_total"]
    fieldsets = (
        ("EVDA", {"fields": ("evda_initiale",)}),
        (
            "Score de Glasgow",
            {
                "fields": (
                    (
                        "score_glasgow_yeux",
                        "score_glasgow_verbal",
                        "score_glasgow_motricite",
                    ),
                    ("score_glasgow_total", "glasgow_qualifie"),
                )
            },
        ),
        ("Examen pupillaire", {"fields": ("nombre_reaction_pupillaire",)}),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


class HistoriqueMedicalInline(SectionsInlineMixin, admin.StackedInline):
    model = HistoriqueMedical
    fieldsets = (
        ("Comorbidités", {"fields": ("nombre_comorbidites",)}),
        ("Patiente enceinte", {"fields": ("patiente_enceinte",)}),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


class TriageInline(SectionsInlineMixin, admin.StackedInline):
    model = Triage
    fieldsets = (
        (
            "Évaluation initiale",
            {
                "fields": (
                    "triage_effectue",
                    "outil_triage",
                    "autre_outil_triage",
                    "autre_categorie_outil_triage",
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


class InterventionsUrgencesMedicamentsLiquideInline(
    SectionsInlineMixin, admin.StackedInline
):
    model = InterventionsUrgencesMedicamentsLiquide
    fieldsets = (
        (
            "Médicaments et liquides",
            {
                "fields": (
                    "medicaments_liquide_administres",
                    "medicaments_liquide_types",
                    "medicaments_liquide_autre",
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


# ==================== ADMINS DES MODÈLES DE RÉFÉRENCE ====================


@admin.register(ProcedureType)
class ProcedureTypeAdmin(admin.ModelAdmin):
    list_display = ["nom", "actif", "description_courte"]
    list_filter = ["actif"]
    search_fields = ["nom", "description"]
    list_editable = ["actif"]
    ordering = ["nom"]

    def description_courte(self, obj):
        if obj.description:
            return (
                obj.description[:50] + "..."
                if len(obj.description) > 50
                else obj.description
            )
        return "-"

    description_courte.short_description = "Description"


@admin.register(DiagnosticTestType)
class DiagnosticTestTypeAdmin(admin.ModelAdmin):
    list_display = ["nom", "actif", "description_courte"]
    list_filter = ["actif"]
    search_fields = ["nom", "description"]
    list_editable = ["actif"]
    ordering = ["nom"]

    def description_courte(self, obj):
        if obj.description:
            return (
                obj.description[:50] + "..."
                if len(obj.description) > 50
                else obj.description
            )
        return "-"

    description_courte.short_description = "Description"


@admin.register(MedicamentType)
class MedicamentTypeAdmin(admin.ModelAdmin):
    list_display = ["nom_medicament", "dosage_standard", "unite_mesure", "actif"]
    list_filter = ["actif", "unite_mesure"]
    search_fields = ["nom_medicament", "description"]
    list_editable = ["actif"]
    ordering = ["nom_medicament"]
    fieldsets = (
        (None, {"fields": ("nom_medicament", "description", "actif")}),
        ("Dosage", {"fields": ("dosage_standard", "unite_mesure")}),
    )


@admin.register(LocalisationType)
class LocalisationTypeAdmin(admin.ModelAdmin):
    list_display = ["nom", "actif"]
    list_filter = ["actif"]
    search_fields = ["nom"]
    list_editable = ["actif"]
    ordering = ["nom"]


@admin.register(ConditionType)
class ConditionTypeAdmin(admin.ModelAdmin):
    list_display = ["nom", "actif"]
    list_filter = ["actif"]
    search_fields = ["nom"]
    list_editable = ["actif"]
    ordering = ["nom"]


@admin.register(Geolocalisation)
class GeolocalisationAdmin(admin.ModelAdmin):
    list_display = ["description", "latitude", "longitude", "coordonnees_display"]
    search_fields = ["description"]
    list_filter = ["latitude", "longitude"]

    def coordonnees_display(self, obj):
        if obj.latitude and obj.longitude:
            return f"({obj.latitude}, {obj.longitude})"
        return "Non défini"

    coordonnees_display.short_description = "Coordonnées"


# ==================== ADMIN PRINCIPAL - DOSSIER MÉDICAL ====================


@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = [
        "numero_dossier",
        "patient_display",
        "hospital",
        "statut_display",
        "date_admission",
        "duree_sejour_display",
        "enregistrator",
    ]
    list_filter = [StatutDossierFilter, HopitalFilter, "date_creation", "dossier_prive"]
    search_fields = [
        "numero_dossier",
        "patient__first_name",
        "patient__last_name",
        "patient__numero_patient",
        "motif_consultation",
    ]
    readonly_fields = [
        "numero_dossier",
        "date_creation",
        "date_modification",
        "duree_sejour_display",
        "sections_completees",
    ]
    date_hierarchy = "date_admission"

    fieldsets = (
        (
            "Informations principales",
            {"fields": ("numero_dossier", "patient", "hospital", "enregistrator")},
        ),
        (
            "Dates et statut",
            {
                "fields": (
                    ("date_admission", "date_sortie"),
                    "statut",
                    "duree_sejour_display",
                )
            },
        ),
        ("Consultation", {"fields": ("motif_consultation", "commentaires_generaux")}),
        # ('Contrôle d\'accès', {
        #     'fields': ('dossier_prive', 'hopitaux_autorises'),
        #     'classes': ('collapse',)
        # }),
        (
            "Métadonnées",
            {
                "fields": ("date_creation", "date_modification", "sections_completees"),
                "classes": ("collapse",),
            },
        ),
    )

    # filter_horizontal = ['hopitaux_autorises']

    inlines = [
        InformationVariantPatientInline,
        SignesVitauxInline,
        EvaluationABCDEInline,
        AutorisationAccesDossierInline,
        HistoriqueMedicalInline,
        TriageInline,
        InterventionsUrgencesMedicamentsLiquideInline,
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("patient", "hospital", "enregistrator")
            .prefetch_related("hopitaux_autorises")
        )

    def patient_display(self, obj):
        if obj.patient:
            return format_html(
                "<strong>{} {}</strong><br><small>ID: {}</small>",
                obj.patient.first_name,
                obj.patient.last_name,
                obj.patient.id,
            )
        return "-"

    patient_display.short_description = "Patient"

    def statut_display(self, obj):
        colors = {
            "ouvert": "#28a745",
            "en_cours": "#ffc107",
            "ferme": "#6c757d",
            "archive": "#343a40",
        }
        color = colors.get(obj.statut, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_statut_display(),
        )

    statut_display.short_description = "Statut"

    def duree_sejour_display(self, obj):
        duree = obj.duree_sejour
        if duree is not None:
            if duree < 24:
                return f"{duree:.1f}h"
            else:
                jours = int(duree // 24)
                heures = duree % 24
                return f"{jours}j {heures:.1f}h"
        elif obj.est_en_cours and obj.date_admission:
            duree_actuelle = (
                timezone.now() - obj.date_admission
            ).total_seconds() / 3600
            return f"{duree_actuelle:.1f}h (en cours)"
        return "-"

    duree_sejour_display.short_description = "Durée séjour"

    def sections_completees(self, obj):
        """Affiche le nombre de sections complétées."""
        sections = [
            obj.informationvariantpatient_sections.exists(),
            obj.signesvitaux_sections.exists(),
            obj.evaluationabcde_sections.exists(),
            obj.triage_sections.exists(),
            obj.historiquemedical_sections.exists(),
            obj.historiquemaladieactuelle_sections.exists(),
            obj.blessures_sections.exists(),
        ]
        completees = sum(sections)
        total = len(sections)
        pourcentage = (completees / total) * 100

        color = (
            "#28a745"
            if pourcentage >= 80
            else "#ffc107" if pourcentage >= 50 else "#dc3545"
        )

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{} ({}%)</span>',
            color,
            completees,
            total,
            int(pourcentage),
        )

    sections_completees.short_description = "Sections complétées"

    actions = ["fermer_dossiers", "archiver_dossiers", "exporter_dossiers"]

    def fermer_dossiers(self, request, queryset):
        updated = queryset.filter(statut__in=["ouvert", "en_cours"]).update(
            statut="ferme", date_sortie=timezone.now()
        )
        self.message_user(request, f"{updated} dossier(s) fermé(s).")

    fermer_dossiers.short_description = "Fermer les dossiers sélectionnés"

    def archiver_dossiers(self, request, queryset):
        updated = queryset.filter(statut="ferme").update(statut="archive")
        self.message_user(request, f"{updated} dossier(s) archivé(s).")

    archiver_dossiers.short_description = "Archiver les dossiers sélectionnés"

    def exporter_dossiers(self, request, queryset):
        # Placeholder pour l'export - à implémenter selon vos besoins
        self.message_user(
            request, f"Export de {queryset.count()} dossier(s) en cours..."
        )

    exporter_dossiers.short_description = "Exporter les dossiers sélectionnés"


# ==================== ADMIN AUTORISATIONS ====================


@admin.register(AutorisationAccesDossier)
class AutorisationAccesDossierAdmin(admin.ModelAdmin):
    list_display = [
        "dossier_numero",
        "hospital_demandeur",
        "hospital_proprietaire",
        "statut_display",
        "demandeur",
        "date_demande",
        "date_reponse",
    ]
    list_filter = [
        "statut",
        "date_demande",
        "hospital_demandeur",
        "hospital_proprietaire",
    ]
    search_fields = [
        "dossier__numero_dossier",
        "dossier__patient__first_name",
        "dossier__patient__last_name",
        "motif_demande",
    ]
    readonly_fields = ["date_demande", "date_reponse"]
    date_hierarchy = "date_demande"

    fieldsets = (
        (
            "Demande",
            {
                "fields": (
                    "dossier",
                    "hospital_demandeur",
                    "demandeur",
                    "motif_demande",
                    "date_demande",
                )
            },
        ),
        (
            "Réponse",
            {
                "fields": (
                    "statut",
                    "approbateur",
                    "date_reponse",
                    "motif_refus",
                    "date_expiration",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "dossier",
                "hospital_demandeur",
                "hospital_proprietaire",
                "demandeur",
                "approbateur",
            )
        )

    def dossier_numero(self, obj):
        return obj.dossier.numero_dossier

    dossier_numero.short_description = "Numéro dossier"

    def statut_display(self, obj):
        colors = {
            "en_attente": "#ffc107",
            "approuvee": "#28a745",
            "refusee": "#dc3545",
            "expiree": "#6c757d",
        }
        color = colors.get(obj.statut, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_statut_display(),
        )

    statut_display.short_description = "Statut"


# ==================== ADMINS DES SECTIONS ====================


class SectionAdminMixin:
    """Mixin pour les admins de sections."""

    list_display = [
        "dossier_numero",
        "patient_nom",
        "hospital",
        "date_creation",
        "enregistre_par",
    ]
    list_filter = ["date_creation", "dossier_medical__hospital"]
    search_fields = [
        "dossier_medical__numero_dossier",
        "dossier_medical__patient__first_name",
        "dossier_medical__patient__last_name",
    ]
    readonly_fields = ["date_creation", "date_modification"]
    date_hierarchy = "date_creation"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "dossier_medical__patient",
                "dossier_medical__hospital",
                "enregistre_par",
            )
        )

    def dossier_numero(self, obj):
        return obj.dossier_medical.numero_dossier

    dossier_numero.short_description = "N° Dossier"

    def patient_nom(self, obj):
        patient = obj.dossier_medical.patient
        if patient:
            return f"{patient.first_name} {patient.last_name}"
        return "-"

    patient_nom.short_description = "Patient"

    def hospital(self, obj):
        return obj.dossier_medical.hospital.name

    hospital.short_description = "Hôpital"


@admin.register(Triage)
class TriageAdmin(SectionAdminMixin, admin.ModelAdmin):
    list_display = SectionAdminMixin.list_display + ["triage_effectue", "outil_triage"]
    list_filter = SectionAdminMixin.list_filter + ["triage_effectue", "outil_triage"]

    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Triage",
            {
                "fields": (
                    "triage_effectue",
                    "outil_triage",
                    "autre_outil_triage",
                    "autre_categorie_outil_triage",
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(HistoriqueMedical)
class HistoriqueMedicalAdmin(SectionAdminMixin, admin.ModelAdmin):
    list_display = SectionAdminMixin.list_display + [
        "nombre_comorbidites",
        "patiente_enceinte",
    ]
    list_filter = SectionAdminMixin.list_filter + ["patiente_enceinte"]

    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Historique médical",
            {"fields": ("nombre_comorbidites", "patiente_enceinte")},
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Blessures)
class BlessuresAdmin(SectionAdminMixin, admin.ModelAdmin):
    list_display = SectionAdminMixin.list_display + [
        "checklist_trauma_utilisee",
        "blessure_supplementaire",
    ]
    list_filter = SectionAdminMixin.list_filter + [
        "checklist_trauma_utilisee",
        "blessure_supplementaire",
    ]

    inlines = [BlessureDetailInline]

    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Évaluation trauma",
            {"fields": ("checklist_trauma_utilisee", "blessure_supplementaire")},
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(BlessureDetail)
class BlessureDetailAdmin(admin.ModelAdmin):
    list_display = ["blessures_record", "localisation", "conditions_display"]
    list_filter = ["localisation", "conditions"]
    search_fields = [
        "blessures_record__dossier_medical__numero_dossier",
        "localisation__nom",
    ]
    filter_horizontal = ["conditions"]

    def conditions_display(self, obj):
        conditions = obj.conditions.all()
        if conditions:
            return ", ".join([c.nom for c in conditions])
        return "Aucune condition"

    conditions_display.short_description = "Conditions"


@admin.register(InterventionsUrgencesMedicamentsLiquide)
class InterventionsUrgencesMedicamentsLiquideAdmin(SectionAdminMixin, admin.ModelAdmin):
    list_display = SectionAdminMixin.list_display + ["medicaments_liquide_administres"]
    list_filter = SectionAdminMixin.list_filter + ["medicaments_liquide_administres"]
    filter_horizontal = ["medicaments_liquide_types"]

    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Médicaments et liquides",
            {
                "fields": (
                    "medicaments_liquide_administres",
                    "medicaments_liquide_types",
                    "medicaments_liquide_autre",
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(InterventionsUrgencesProcedures)
class InterventionsUrgencesProceduresAdmin(SectionAdminMixin, admin.ModelAdmin):
    list_display = SectionAdminMixin.list_display + ["procedures"]
    list_filter = SectionAdminMixin.list_filter + ["procedures"]
    filter_horizontal = ["procedures_types"]

    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Procédures",
            {"fields": ("procedures", "procedures_types", "procedures_autre")},
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(InterventionsUrgencesTestsDiagnostiques)
class InterventionsUrgencesTestsDiagnostiquesAdmin(SectionAdminMixin, admin.ModelAdmin):
    list_display = SectionAdminMixin.list_display + ["tests_diagnostiques"]
    list_filter = SectionAdminMixin.list_filter + ["tests_diagnostiques"]
    filter_horizontal = ["tests_diagnostiques_types"]

    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Tests diagnostiques",
            {
                "fields": (
                    "tests_diagnostiques",
                    "tests_diagnostiques_types",
                    "tests_diagnostiques_autre",
                )
            },
        ),
        (
            "Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(DispositionUniteUrgence)
class DispositionUniteUrgenceAdmin(SectionAdminMixin, admin.ModelAdmin):
    # --- Affichage dans la liste ---
    list_display = SectionAdminMixin.list_display + [
        "sortie_su",
        "date_sortie_unite_urgence",
        "heure_sortie_unite_urgence",
    ]
    list_filter = SectionAdminMixin.list_filter + [
        "sortie_su",
        "date_sortie_unite_urgence",
    ]
    readonly_fields = ('date_sortie_unite_urgence', 'heure_sortie_unite_urgence','date_creation','date_modification')
    # --- Organisation du formulaire de détails ---
    fieldsets = (
        ("Dossier", {"fields": ("dossier_medical",)}),
        (
            "Disposition de Sortie",
            {
                "fields": (
                    ("date_sortie_unite_urgence", "heure_sortie_unite_urgence"),
                    "sortie_su",
                )
            },
        ),
        # Chaque section ci-dessous est conditionnelle
        (
            "Détails : Autre",
            {
                "fields": ("autre_sortie_su",),
                # 'classes' est la clé : ce nom de classe sera utilisé par le JS
                "classes": ("collapse", "dynamic-fieldset", "dynamic-autre"),
            },
        ),
        (
            "Détails : Retour à Domicile",
            {
                "fields": ("consignes_domicile", "accompagnant", "rdv_controle"),
                "classes": ("collapse", "dynamic-fieldset", "dynamic-domicile"),
            },
        ),
        (
            "Détails : Hospitalisation",
            {
                "fields": ("diagnostique_hospitalisation", "numero_chambre_lit"),
                "classes": ("collapse", "dynamic-fieldset", "dynamic-hospitalisation"),
            },
        ),
        (
            "Détails : Transfert",
            {
                "fields": (
                    "hopital_transfert",
                    "autre_hopital",
                    "service_transfert",
                    "autre_service_transfert",
                    "motif_transfert",
                ),
                "classes": ("collapse", "dynamic-fieldset", "dynamic-transfert"),
            },
        ),
        (
            "Détails : Décès",
            {
                "fields": ("cause_deces",),
                "classes": ("collapse", "dynamic-fieldset", "dynamic-deces"),
            },
        ),
        (
            "Informations Système",
            {
                "fields": ("enregistre_par", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )


# ==================== CONFIGURATION GLOBALE ====================

# Personnalisation du site admin
admin.site.site_header = "Administration - Système de Gestion Médicale"
admin.site.site_title = "SGM Admin"
admin.site.index_title = "Tableau de bord administrateur"

# Enregistrement des modèles restants (si pas déjà fait)
models_restants = [
    HistoriqueMaladieActuelle,
    InformationVariantPatient,
    SignesVitaux,
    EvaluationABCDE,
]

for model in models_restants:
    if not admin.site.is_registered(model):
        admin.site.register(
            model,
            type(f"{model.__name__}Admin", (SectionAdminMixin, admin.ModelAdmin), {}),
        )
