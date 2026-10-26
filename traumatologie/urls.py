from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProcedureTypeViewSet,
    DiagnosticTestTypeViewSet,
    MedicamentTypeViewSet,
    LocalisationTypeViewSet,
    ConditionTypeViewSet,
    GeolocalisationViewSet,
    DossierMedicalViewSet,
    AutorisationAccesDossierViewSet,
    InformationVariantPatientViewSet,
    SignesVitauxViewSet,
    EvaluationABCDEViewSet,
    TriageViewSet,
    HistoriqueMedicalViewSet,
    HistoriqueMaladieActuelleViewSet,
    BlessuresViewSet,
    BlessureDetailViewSet,
    InterventionsUrgencesMedicamentsLiquideViewSet,
    InterventionsUrgencesProceduresViewSet,
    InterventionsUrgencesTestsDiagnostiquesViewSet,
    DispositionUniteUrgenceViewSet,
)

router = DefaultRouter()
# Référentiels
router.register(r'procedure-types', ProcedureTypeViewSet, basename='proceduretype')
router.register(r'diagnostic-test-types', DiagnosticTestTypeViewSet, basename='diagnostictesttype')
router.register(r'medicament-types', MedicamentTypeViewSet, basename='medicamenttype')
router.register(r'localisation-types', LocalisationTypeViewSet, basename='localisationtype')
router.register(r'condition-types', ConditionTypeViewSet, basename='conditiontype')
router.register(r'geolocalisations', GeolocalisationViewSet, basename='geolocalisation')

# Dossiers médicaux
router.register(r'traumatologie-dossiers', DossierMedicalViewSet, basename='dossiermedical')

# Autorisations d'accès
router.register(r'autorisations-dossiers', AutorisationAccesDossierViewSet, basename='autorisationaccesdossier')

# Sections de dossier
router.register(r'information-variant-patient', InformationVariantPatientViewSet, basename='informationvariantpatient')
router.register(r'signes-vitaux', SignesVitauxViewSet, basename='signesvitaux')
router.register(r'evaluation-abcde', EvaluationABCDEViewSet, basename='evaluationabcde')
router.register(r'triage', TriageViewSet, basename='triage')
router.register(r'historique-medical', HistoriqueMedicalViewSet, basename='historiquemedical')
router.register(r'historique-maladie-actuelle', HistoriqueMaladieActuelleViewSet, basename='historiquemaladieactuelle')
router.register(r'blessures', BlessuresViewSet, basename='blessures')
router.register(r'blessure-details', BlessureDetailViewSet, basename='blessuredetail')
router.register(r'interventions-medicaments-liquide', InterventionsUrgencesMedicamentsLiquideViewSet, basename='interventionsmedicamentsliquide')
router.register(r'interventions-procedures', InterventionsUrgencesProceduresViewSet, basename='interventionsprocedures')
router.register(r'interventions-tests-diagnostiques', InterventionsUrgencesTestsDiagnostiquesViewSet, basename='interventionstestsdiagnostiques')
router.register(r'disposition-unite-urgence', DispositionUniteUrgenceViewSet, basename='dispositionuniteurgence')

urlpatterns = [
    path('', include(router.urls)),
]