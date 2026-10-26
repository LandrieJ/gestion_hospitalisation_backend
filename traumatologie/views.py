from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import PermissionDenied
from django.db import transaction

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

from .serializers import (
    # Serializers de référence
    ProcedureTypeSerializer,
    DiagnosticTestTypeSerializer,
    MedicamentTypeSerializer,
    LocalisationTypeSerializer,
    ConditionTypeSerializer,
    GeolocalisationSerializer,
    # Serializers principaux
    DossierMedicalListSerializer,
    DossierMedicalDetailSerializer,
    DossierMedicalCreateUpdateSerializer,
    AutorisationAccesDossierSerializer,
    # Serializers des sections
    InformationVariantPatientSerializer,
    SignesVitauxSerializer,
    EvaluationABCDESerializer,
    TriageSerializer,
    HistoriqueMedicalSerializer,
    HistoriqueMaladieActuelleSerializer,
    BlessuresSerializer,
    BlessureDetailSerializer,
    InterventionsUrgencesMedicamentsLiquideSerializer,
    InterventionsUrgencesProceduresSerializer,
    InterventionsUrgencesTestsDiagnostiquesSerializer,
    DispositionUniteUrgenceSerializer,
)

from patient.models import Patient
from comptes.models import CustomUser, Hospital


# ==================== PERMISSIONS PERSONNALISÉES ====================

class DossierMedicalPermission(permissions.BasePermission):
    """
    Permission personnalisée pour les dossiers médicaux.
    - L'utilisateur doit être authentifié
    - Pour la lecture : accès si l'utilisateur travaille dans l'hôpital du dossier
      ou si son hôpital a une autorisation d'accès
    - Pour l'écriture : accès uniquement si l'utilisateur travaille dans l'hôpital du dossier
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur a un hôpital associé
        if not hasattr(user, 'hospital') or not user.hospital:
            return False

        # Pour les méthodes de lecture (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            # Accès direct si même hôpital
            if user.hospital == obj.hospital:
                return True
            
            # Accès via autorisation
            return obj.hopitaux_autorises.filter(id=user.hospital.id).exists()
        
        # Pour les méthodes d'écriture, seul l'hôpital propriétaire peut modifier
        return user.hospital == obj.hospital


# ==================== VIEWSETS DE RÉFÉRENCE ====================

class ProcedureTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de procédures (lecture seule)."""
    queryset = ProcedureType.objects.filter(actif=True)
    serializer_class = ProcedureTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom']
    ordering = ['nom']


class DiagnosticTestTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de tests diagnostiques (lecture seule)."""
    queryset = DiagnosticTestType.objects.filter(actif=True)
    serializer_class = DiagnosticTestTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom']
    ordering = ['nom']


class MedicamentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de médicaments (lecture seule)."""
    queryset = MedicamentType.objects.filter(actif=True)
    serializer_class = MedicamentTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom_medicament', 'description']
    ordering_fields = ['nom_medicament']
    ordering = ['nom_medicament']


class LocalisationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de localisation anatomique (lecture seule)."""
    queryset = LocalisationType.objects.filter(actif=True)
    serializer_class = LocalisationTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom']
    ordering = ['nom']


class ConditionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de conditions (lecture seule)."""
    queryset = ConditionType.objects.filter(actif=True)
    serializer_class = ConditionTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom']
    ordering = ['nom']


class GeolocalisationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la géolocalisation."""
    queryset = Geolocalisation.objects.all()
    serializer_class = GeolocalisationSerializer
    permission_classes = [IsAuthenticated]


# ==================== VIEWSET PRINCIPAL - DOSSIER MÉDICAL ====================

class DossierMedicalViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour gérer les dossiers médicaux.
    Gère la création, lecture, mise à jour et suppression des dossiers complets.
    """
    permission_classes = [DossierMedicalPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['statut', 'hospital', 'patient']
    search_fields = ['numero_dossier', 'patient__first_name', 'patient__last_name', 'motif_consultation']
    ordering_fields = ['date_creation', 'date_admission', 'numero_dossier']
    ordering = ['-date_creation']

    def get_queryset(self):
        """
        Retourne les dossiers auxquels l'utilisateur a accès.
        """
        user = self.request.user
        
        if not hasattr(user, 'hospital') or not user.hospital:
            return DossierMedical.objects.none()
        
        queryset = DossierMedical.objects.select_related('patient', 'hospital', 'enregistrator').prefetch_related(
            'informationvariantpatient_sections',
            'signesvitaux_sections',
            'evaluationabcde_sections',
            'triage_sections',
            'historiquemedical_sections',
            'historiquemaladieactuelle_sections',
            'blessures_sections__details__localisation',
            'blessures_sections__details__conditions',
            'interventionsurgencesmedicamentsliquide_sections__medicaments_liquide_types',
            'interventionsurgencesprocedures_sections__procedures_types',
            'interventionsurgencestestsdiagnostiques_sections__tests_diagnostiques_types',
            'dispositionuniteurgence_sections',
        )

        # Filtrer selon les permissions
        return queryset.filter(
            Q(hospital=user.hospital) |  # Dossiers de son hôpital
            Q(hopitaux_autorises=user.hospital)  # Dossiers autorisés
        ).distinct()

    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action."""
        if self.action == 'list':
            return DossierMedicalListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DossierMedicalCreateUpdateSerializer
        else:
            return DossierMedicalDetailSerializer

    def perform_create(self, serializer):
        """Personnalise la création d'un dossier."""
        user = self.request.user
        
        # S'assurer que l'enregistreur est l'utilisateur actuel
        serializer.save(enregistrator=user)

    def perform_update(self, serializer):
        """Personnalise la mise à jour d'un dossier."""
        # Vérifier que l'utilisateur peut modifier ce dossier
        if not self.request.user.hospital == serializer.instance.hospital:
            raise PermissionDenied("Vous ne pouvez modifier que les dossiers de votre hôpital.")
        
        serializer.save()

    @action(detail=True, methods=['post'])
    def fermer_dossier(self, request, pk=None):
        """Action pour fermer un dossier."""
        dossier = self.get_object()
        
        if dossier.statut == DossierMedical.StatutDossier.FERME:
            return Response(
                {'error': 'Le dossier est déjà fermé.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dossier.statut = DossierMedical.StatutDossier.FERME
        dossier.date_sortie = timezone.now()
        dossier.save()
        
        serializer = self.get_serializer(dossier)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archiver_dossier(self, request, pk=None):
        """Action pour archiver un dossier."""
        dossier = self.get_object()
        
        if dossier.statut != DossierMedical.StatutDossier.FERME:
            return Response(
                {'error': 'Seuls les dossiers fermés peuvent être archivés.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dossier.statut = DossierMedical.StatutDossier.ARCHIVE
        dossier.save()
        
        serializer = self.get_serializer(dossier)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mes_dossiers_recents(self, request):
        """Retourne les dossiers récents créés par l'utilisateur."""
        dossiers = self.get_queryset().filter(
            enregistrator=request.user
        )[:10]  # 10 derniers dossiers
        
        serializer = DossierMedicalListSerializer(dossiers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Retourne des statistiques sur les dossiers."""
        queryset = self.get_queryset()
        
        stats = {
            'total_dossiers': queryset.count(),
            'dossiers_ouverts': queryset.filter(
                statut__in=[DossierMedical.StatutDossier.OUVERT, DossierMedical.StatutDossier.EN_COURS]
            ).count(),
            'dossiers_fermes': queryset.filter(statut=DossierMedical.StatutDossier.FERME).count(),
            'dossiers_archives': queryset.filter(statut=DossierMedical.StatutDossier.ARCHIVE).count(),
            'dossiers_cette_semaine': queryset.filter(
                date_creation__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }
        
        return Response(stats)

class SectionDossierMixin:
    """Mixin pour les vues des sections de dossier."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtre selon les dossiers accessibles à l'utilisateur."""
        user = self.request.user
        
        if not hasattr(user, 'hospital') or not user.hospital:
            return self.queryset.none()

        # Filtrer selon les dossiers accessibles
        return self.queryset.filter(
            Q(dossier_medical__hospital=user.hospital) |
            Q(dossier_medical__hopitaux_autorises=user.hospital)
        ).distinct()

    def perform_create(self, serializer):
        """S'assurer que l'enregistreur est l'utilisateur actuel."""
        serializer.save(enregistre_par=self.request.user)


class InformationVariantPatientViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour les informations variant patient."""
    queryset = InformationVariantPatient.objects.select_related('dossier_medical', 'geolocalisation')
    serializer_class = InformationVariantPatientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'mode_arrivee', 'classification_profession']


class SignesVitauxViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour les signes vitaux."""
    queryset = SignesVitaux.objects.select_related('dossier_medical')
    serializer_class = SignesVitauxSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'signes_de_vie', 'administration_oxygene']


class EvaluationABCDEViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour l'évaluation ABCDE."""
    queryset = EvaluationABCDE.objects.select_related('dossier_medical')
    serializer_class = EvaluationABCDESerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['dossier_medical', 'evda_initiale', 'glasgow_qualifie']
    ordering_fields = ['score_glasgow_total']


class TriageViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour le triage."""
    queryset = Triage.objects.select_related('dossier_medical')
    serializer_class = TriageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'triage_effectue', 'outil_triage']


class HistoriqueMedicalViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour l'historique médical."""
    queryset = HistoriqueMedical.objects.select_related('dossier_medical')
    serializer_class = HistoriqueMedicalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'patiente_enceinte']


class HistoriqueMaladieActuelleViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour l'historique de la maladie actuelle."""
    queryset = HistoriqueMaladieActuelle.objects.select_related('dossier_medical')
    serializer_class = HistoriqueMaladieActuelleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'intentionnel', 'soins_prehospitaliers']


class BlessuresViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour les blessures."""
    queryset = Blessures.objects.select_related('dossier_medical').prefetch_related(
        'details__localisation', 'details__conditions'
    )
    serializer_class = BlessuresSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'checklist_trauma_utilisee', 'blessure_supplementaire']


class BlessureDetailViewSet(viewsets.ModelViewSet):
    """ViewSet pour les détails de blessures."""
    queryset = BlessureDetail.objects.select_related(
        'blessures_record', 'localisation'
    ).prefetch_related('conditions')
    serializer_class = BlessureDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blessures_record', 'localisation']


class InterventionsUrgencesMedicamentsLiquideViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour les interventions médicaments/liquides."""
    queryset = InterventionsUrgencesMedicamentsLiquide.objects.select_related(
        'dossier_medical'
    ).prefetch_related('medicaments_liquide_types')
    serializer_class = InterventionsUrgencesMedicamentsLiquideSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'medicaments_liquide_administres']


class InterventionsUrgencesProceduresViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour les interventions procédures."""
    queryset = InterventionsUrgencesProcedures.objects.select_related(
        'dossier_medical'
    ).prefetch_related('procedures_types')
    serializer_class = InterventionsUrgencesProceduresSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'procedures']


class InterventionsUrgencesTestsDiagnostiquesViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour les interventions tests diagnostiques."""
    queryset = InterventionsUrgencesTestsDiagnostiques.objects.select_related(
        'dossier_medical'
    ).prefetch_related('tests_diagnostiques_types')
    serializer_class = InterventionsUrgencesTestsDiagnostiquesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical', 'tests_diagnostiques']


class DispositionUniteUrgenceViewSet(SectionDossierMixin, viewsets.ModelViewSet):
    """ViewSet pour la disposition unité d'urgence."""
    queryset = DispositionUniteUrgence.objects.select_related('dossier_medical')
    serializer_class = DispositionUniteUrgenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dossier_medical','sortie_su']


# ==================== VIEWSET POUR LES AUTORISATIONS D'ACCÈS ====================

class AutorisationAccesDossierViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les autorisations d'accès aux dossiers."""
    serializer_class = AutorisationAccesDossierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['statut', 'hospital_demandeur', 'hospital_proprietaire']
    ordering_fields = ['date_demande', 'date_reponse']
    ordering = ['-date_demande']

    def get_queryset(self):
        """Retourne les autorisations liées à l'hôpital de l'utilisateur."""
        user = self.request.user
        
        if not hasattr(user, 'hospital') or not user.hospital:
            return AutorisationAccesDossier.objects.none()

        # Autorisations où l'hôpital de l'utilisateur est demandeur ou propriétaire
        return AutorisationAccesDossier.objects.select_related(
            'dossier', 'hospital_demandeur', 'hospital_proprietaire', 'demandeur', 'approbateur'
        ).filter(
            Q(hospital_demandeur=user.hospital) | 
            Q(hospital_proprietaire=user.hospital)
        )

    def perform_create(self, serializer):
        """Crée une nouvelle demande d'autorisation."""
        user = self.request.user
        dossier = serializer.validated_data['dossier']
        
        # S'assurer que l'utilisateur demande pour son hôpital
        serializer.save(
            hospital_demandeur=user.hospital,
            hospital_proprietaire=dossier.hospital,
            demandeur=user
        )

    @action(detail=True, methods=['post'])
    def approuver(self, request, pk=None):
        autorisation = self.get_object()
        if request.user.hospital != autorisation.hospital_proprietaire:
            raise PermissionDenied("Vous ne pouvez approuver que les demandes concernant votre hôpital.")
        if autorisation.statut != AutorisationAccesDossier.StatutDemande.EN_ATTENTE:
            return Response({'error': 'Cette demande a déjà été traitée.'}, status=status.HTTP_400_BAD_REQUEST)
        if autorisation.dossier.hopitaux_autorises.filter(id=autorisation.hospital_demandeur.id).exists():
            return Response({'error': 'Hôpital déjà autorisé.'}, status=status.HTTP_400_BAD_REQUEST)
        autorisation.statut = AutorisationAccesDossier.StatutDemande.APPROUVEE
        autorisation.approbateur = request.user
        autorisation.date_reponse = timezone.now()
        autorisation.save()
        autorisation.dossier.hopitaux_autorises.add(autorisation.hospital_demandeur)
        serializer = self.get_serializer(autorisation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def refuser(self, request, pk=None):
        """Refuse une demande d'autorisation."""
        autorisation = self.get_object()
        
        # Vérifier que l'utilisateur peut refuser (hôpital propriétaire)
        if request.user.hospital != autorisation.hospital_proprietaire:
            raise PermissionDenied("Vous ne pouvez refuser que les demandes concernant votre hôpital.")
        
        if autorisation.statut != AutorisationAccesDossier.StatutDemande.EN_ATTENTE:
            return Response(
                {'error': 'Cette demande a déjà été traitée.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer le motif de refus
        motif_refus = request.data.get('motif_refus', '')
        if not motif_refus:
            return Response(
                {'error': 'Un motif de refus est requis.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Refuser la demande
        autorisation.statut = AutorisationAccesDossier.StatutDemande.REFUSEE
        autorisation.approbateur = request.user
        autorisation.date_reponse = timezone.now()
        autorisation.motif_refus = motif_refus
        autorisation.save()
        
        serializer = self.get_serializer(autorisation)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def demandes_en_attente(self, request):
        """Retourne les demandes d'autorisation en attente pour l'hôpital de l'utilisateur."""
        demandes = self.get_queryset().filter(
            hospital_proprietaire=request.user.hospital,
            statut=AutorisationAccesDossier.StatutDemande.EN_ATTENTE
        )
        
        serializer = self.get_serializer(demandes, many=True)
        return Response(serializer.data)