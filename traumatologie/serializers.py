from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import datetime, time
from decimal import Decimal

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

from patient.models import Patient
from comptes.models import CustomUser
from hospital.models import Hospital
from service.models import Service


# ==================== SERIALIZERS DE RÉFÉRENCE ====================


class ProcedureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureType
        fields = ["id", "nom", "description", "actif"]


class DiagnosticTestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTestType
        fields = ["id", "nom", "description", "actif"]


class MedicamentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicamentType
        fields = [
            "id",
            "nom_medicament",
            "description",
            "dosage_standard",
            "unite_mesure",
            "actif",
        ]


class LocalisationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalisationType
        fields = ["id", "nom", "actif"]


class ConditionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionType
        fields = ["id", "nom", "actif"]


class GeolocalisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geolocalisation
        fields = ["id", "latitude", "longitude", "description"]

    def create(self, validated_data):
        # Gestion de la création de géolocalisation depuis le formData
        return Geolocalisation.objects.create(**validated_data)


# ==================== SERIALIZERS DES SECTIONS ====================


class InformationVariantPatientSerializer(serializers.ModelSerializer):
    geolocalisation = GeolocalisationSerializer(required=False, allow_null=True)

    class Meta:
        model = InformationVariantPatient
        fields = [
            "mode_arrivee",
            "autre_mode_arrivee",
            "nombre_frequentations_medicales",
            "classification_profession",
            "profession_specifique",
            "domicile",
            "residence_secondaire",
            "lieu_accident",
            "geolocalisation",
            "accident_de_masse",
        ]

    def validate_geolocalisation(self, value):
        if value.get("latitude") and (
            value["latitude"] < -90 or value["latitude"] > 90
        ):
            raise serializers.ValidationError("Latitude doit être entre -90 et 90.")
        if value.get("longitude") and (
            value["longitude"] < -180 or value["longitude"] > 180
        ):
            raise serializers.ValidationError("Longitude doit être entre -180 et 180.")
        return value

    def create(self, validated_data):
        geolocalisation_data = validated_data.pop("geolocalisation", None)

        if geolocalisation_data:
            geolocalisation = Geolocalisation.objects.create(**geolocalisation_data)
            validated_data["geolocalisation"] = geolocalisation

        return InformationVariantPatient.objects.create(**validated_data)


class SignesVitauxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignesVitaux
        fields = [
            "signes_de_vie",
            "pression_arterielle_systolique",
            "pression_arterielle_diastolique",
            "frequence_cardiaque",
            "saturation_oxygene",
            "administration_oxygene",
            "frequence_respiratoire",
        ]


class EvaluationABCDESerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationABCDE
        fields = [
            "evda_initiale",
            "score_glasgow_yeux",
            "score_glasgow_verbal",
            "score_glasgow_motricite",
            "score_glasgow_total",
            "glasgow_qualifie",
            "nombre_reaction_pupillaire",
        ]
        read_only_fields = ["score_glasgow_total"]  # Calculé automatiquement


class TriageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Triage
        fields = [
            "triage_effectue",
            "outil_triage",
            "autre_outil_triage",
            "autre_categorie_outil_triage",
        ]


class HistoriqueMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueMedical
        fields = ["nombre_comorbidites", "patiente_enceinte"]


class HistoriqueMaladieActuelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueMaladieActuelle
        fields = [
            "date_accident",
            "hma_lieu_accident",
            "autre_lieu_accident",
            "activite_lors_accident",
            "autre_activite_lors_accident",
            "mecanisme_accident",
            "autre_mecanisme_accident",
            "materiel_protection",
            "autre_materiel_protection",
            "mecanisme_supplementaire",
            "protection_utilisee",
            "intentionnel",
            "soins_prehospitaliers",
            "prise_en_charge_medical_lieu_accident_lors_transport",
            "hma_autre_mode_arrivee",
            "procedure_supplementaire",
            "consommation_substance",
            "consommation_alcool",
        ]


class BlessureDetailSerializer(serializers.ModelSerializer):
    localisation_nom = serializers.CharField(source="localisation.nom", read_only=True)
    conditions_noms = serializers.StringRelatedField(
        source="conditions", many=True, read_only=True
    )

    class Meta:
        model = BlessureDetail
        fields = [
            "id",
            "localisation",
            "localisation_nom",
            "conditions",
            "conditions_noms",
        ]


class BlessuresSerializer(serializers.ModelSerializer):
    details = BlessureDetailSerializer(many=True, required=False)

    class Meta:
        model = Blessures
        fields = ["checklist_trauma_utilisee", "blessure_supplementaire", "details"]

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])
        blessures = Blessures.objects.create(**validated_data)

        for detail_data in details_data:
            conditions_data = detail_data.pop("conditions", [])
            detail = BlessureDetail.objects.create(
                blessures_record=blessures, **detail_data
            )
            if conditions_data:
                detail.conditions.set(conditions_data)

        return blessures


class InterventionsUrgencesMedicamentsLiquideSerializer(serializers.ModelSerializer):
    medicaments_liquide_types_noms = serializers.StringRelatedField(
        source="medicaments_liquide_types", many=True, read_only=True
    )

    class Meta:
        model = InterventionsUrgencesMedicamentsLiquide
        fields = [
            "medicaments_liquide_administres",
            "medicaments_liquide_types",
            "medicaments_liquide_types_noms",
            "medicaments_liquide_autre",
        ]


class InterventionsUrgencesProceduresSerializer(serializers.ModelSerializer):
    procedures_types_noms = serializers.StringRelatedField(
        source="procedures_types", many=True, read_only=True
    )

    class Meta:
        model = InterventionsUrgencesProcedures
        fields = [
            "procedures",
            "procedures_types",
            "procedures_types_noms",
            "procedures_autre",
        ]


class InterventionsUrgencesTestsDiagnostiquesSerializer(serializers.ModelSerializer):
    tests_diagnostiques_types_noms = serializers.StringRelatedField(
        source="tests_diagnostiques_types", many=True, read_only=True
    )

    class Meta:
        model = InterventionsUrgencesTestsDiagnostiques
        fields = [
            "tests_diagnostiques",
            "tests_diagnostiques_types",
            "tests_diagnostiques_types_noms",
            "tests_diagnostiques_autre",
        ]


class DispositionUniteUrgenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispositionUniteUrgence
        fields = [
            "sortie_su",
            "heure_sortie_unite_urgence",
            "date_sortie_unite_urgence",
            "autre_sortie_su",
            "consignes_domicile",
            "accompagnant",
            "rdv_controle",
            "diagnostique_hospitalisation",
            "numero_chambre_lit",
            "hopital_transfert",
            "autre_hopital",
            "service_transfert",
            "autre_service_transfert",
            "motif_transfert",
            "cause_deces",
        ]


# ==================== SERIALIZER PRINCIPAL - DOSSIER MÉDICAL ====================


class DossierMedicalListSerializer(serializers.ModelSerializer):
    """Serializer pour les listes de dossiers (optimisé)."""

    patient_nom = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    hospital_nom = serializers.CharField(source="hospital.name", read_only=True)
    enregistrator_nom = serializers.SerializerMethodField()
    duree_sejour = serializers.ReadOnlyField()
    est_en_cours = serializers.ReadOnlyField()

    class Meta:
        model = DossierMedical
        fields = [
            "id",
            "patient_id",
            "numero_dossier",
            "patient_nom",
            "hospital_nom",
            "enregistrator_nom",
            "date_creation",
            "date_admission",
            "suite_procedure",
            "date_sortie",
            "statut",
            "duree_sejour",
            "est_en_cours",
            "motif_consultation",
        ]

    def get_patient_nom(self, obj):
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return None
    
    def get_patient_id(self, obj):
        if obj.patient:
            return obj.patient.id
        return None

    def get_enregistrator_nom(self, obj):
        if obj.enregistrator:
            return f"{obj.enregistrator.first_name} {obj.enregistrator.last_name}"
        return None


class DossierMedicalDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un dossier avec toutes ses sections."""

    # Relations de base (lecture seule pour l'affichage)
    patient = serializers.StringRelatedField(read_only=True)
    hospital = serializers.StringRelatedField(read_only=True)
    service = serializers.StringRelatedField(read_only=True)
    enregistrator = serializers.StringRelatedField(read_only=True)

    # Propriétés calculées
    duree_sejour = serializers.ReadOnlyField()
    est_en_cours = serializers.ReadOnlyField()

    # Sections (lecture seule dans ce serializer)
    information_variant_patient = InformationVariantPatientSerializer(
        source="informationvariantpatient_sections.first", read_only=True
    )
    signes_vitaux = SignesVitauxSerializer(
        source="signesvitaux_sections.first", read_only=True
    )
    evaluation_abcde = EvaluationABCDESerializer(
        source="evaluationabcde_sections.first", read_only=True
    )
    triage = TriageSerializer(source="triage_sections.first", read_only=True)
    historique_medical = HistoriqueMedicalSerializer(
        source="historiquemedical_sections.first", read_only=True
    )
    historique_maladie_actuelle = HistoriqueMaladieActuelleSerializer(
        source="historiquemaladieactuelle_sections.first", read_only=True
    )
    blessures = BlessuresSerializer(source="blessures_sections.first", read_only=True)
    interventions_medicaments_liquide = (
        InterventionsUrgencesMedicamentsLiquideSerializer(
            source="interventionsurgencesmedicamentsliquide_sections.first",
            read_only=True,
        )
    )
    interventions_procedures = InterventionsUrgencesProceduresSerializer(
        source="interventionsurgencesprocedures_sections.first", read_only=True
    )
    interventions_tests_diagnostiques = (
        InterventionsUrgencesTestsDiagnostiquesSerializer(
            source="interventionsurgencestestsdiagnostiques_sections.first",
            read_only=True,
        )
    )
    disposition_unite_urgence = DispositionUniteUrgenceSerializer(
        source="dispositionuniteurgence_sections.first", read_only=True
    )

    class Meta:
        model = DossierMedical
        fields = [
            "id",
            "numero_dossier",
            "patient",
            "hospital",
            "service",
            "patient_id",
            "enregistrator",
            "date_creation",
            "date_modification",
            "date_admission",
            "suite_procedure",
            "date_sortie",
            "statut",
            "dossier_prive",
            "motif_consultation",
            "commentaires_generaux",
            "duree_sejour",
            "est_en_cours",
            # Sections
            "information_variant_patient",
            "signes_vitaux",
            "evaluation_abcde",
            "triage",
            "historique_medical",
            "historique_maladie_actuelle",
            "blessures",
            "interventions_medicaments_liquide",
            "interventions_procedures",
            "interventions_tests_diagnostiques",
            "disposition_unite_urgence",
        ]


class DossierMedicalCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour créer/modifier un dossier complet
    """

    information_variant_patient_data = InformationVariantPatientSerializer(
        required=False
    )
    signes_vitaux_data = SignesVitauxSerializer(required=False)
    evaluation_abcde_data = EvaluationABCDESerializer(required=False)
    triage_data = TriageSerializer(required=False)
    historique_medical_data = HistoriqueMedicalSerializer(required=False)
    historique_maladie_actuelle_data = HistoriqueMaladieActuelleSerializer(
        required=False
    )
    blessures_data = BlessuresSerializer(required=False)
    interventions_urgences_medicaments_liquide_data = (
        InterventionsUrgencesMedicamentsLiquideSerializer(required=False)
    )
    interventions_urgences_procedures_data = InterventionsUrgencesProceduresSerializer(
        required=False
    )
    interventions_urgences_tests_diagnostiques_data = (
        InterventionsUrgencesTestsDiagnostiquesSerializer(required=False)
    )
    disposition_unite_urgence_data = DispositionUniteUrgenceSerializer(required=False)

    class Meta:
        model = DossierMedical
        fields = [
            "patient",
            "hospital",
            "service",
            "enregistrator",
            "date_admission",
            "suite_procedure",
            "motif_consultation",
            "commentaires_generaux",
            # Données des sections (compatibles avec formData)
            "information_variant_patient_data",
            "signes_vitaux_data",
            "evaluation_abcde_data",
            "triage_data",
            "historique_medical_data",
            "historique_maladie_actuelle_data",
            "blessures_data",
            "interventions_urgences_medicaments_liquide_data",
            "interventions_urgences_procedures_data",
            "interventions_urgences_tests_diagnostiques_data",
            "disposition_unite_urgence_data",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if hasattr(request.user, "hospital"):
                self.fields["hospital"].queryset = Hospital.objects.filter(id=request.user.hospital.id)
                self.fields["service"].queryset = Service.objects.filter(id=request.user.service.id)

    def validate(self, data):
        """Validations personnalisées."""

        # Validation des IDs depuis le formData
        patient_id = data.get("patient") or self.initial_data.get("patient_id")
        hospital_id = data.get("hospital") or self.initial_data.get("hospital_id")
        service_id = data.get("service") or self.initial_data.get("service_id")
        enregistrator_id = data.get("enregistrator") or self.initial_data.get(
            "enregistrator_id"
        )

        if patient_id:
            try:
                patient = patient_id
                data["patient"] = patient
            except Patient.DoesNotExist:
                raise serializers.ValidationError({"patient": "Patient non trouvé."})

        if hospital_id:
            try:
                hospital = hospital_id
                data["hospital"] = hospital
            except Hospital.DoesNotExist:
                raise serializers.ValidationError({"hospital": "Hôpital non trouvé."})
            
        if service_id:
            try:
                service = service_id
                data["service"] = service
            except Hospital.DoesNotExist:
                raise serializers.ValidationError({"service": "Service non trouvé."})

        if enregistrator_id:
            try:
                enregistrator = enregistrator_id
                data["enregistrator"] = enregistrator
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    {"enregistrator": "Enregistreur non trouvé."}
                )

        disposition_data = data.get("disposition_unite_urgence_data")
        if disposition_data and "sortie_su" in disposition_data:
            suite_procedure = disposition_data["sortie_su"]
            if suite_procedure in [choice[0] for choice in DispositionUniteUrgence.SortieSuChoices.choices]:
                data["suite_procedure"] = suite_procedure
            else:
                raise serializers.ValidationError(
                    {
                        "disposition_unite_urgence_data": "Valeur de 'sortie_su' non valide."
                    }
                )

        # Vérifier si les données de date sont présentes ET non nulles
        if not data.get("date_admission"):
            data["date_admission"] = timezone.now()
        else:
            # Si elle est fournie, s'assurer qu'elle est timezone-aware
            if isinstance(data["date_admission"], datetime) and timezone.is_naive(
                data["date_admission"]
            ):
                data["date_admission"] = timezone.make_aware(data["date_admission"])

        return data

    def _create_sections(self, dossier, sections_data):
        """Crée toutes les sections du dossier."""

        user = self.context.get("request").user if self.context.get("request") else None

        # Information Variant Patient
        if sections_data.get("information_variant_patient_data"):
            self._create_information_variant_patient(
                dossier, sections_data["information_variant_patient_data"], user
            )

        # Signes Vitaux
        if sections_data.get("signes_vitaux_data"):
            SignesVitaux.objects.create(
                dossier_medical=dossier,
                enregistre_par=user,
                **sections_data["signes_vitaux_data"],
            )

        # Evaluation ABCDE
        if sections_data.get("evaluation_abcde_data"):
            EvaluationABCDE.objects.create(
                dossier_medical=dossier,
                enregistre_par=user,
                **sections_data["evaluation_abcde_data"],
            )

        # Triage
        if sections_data.get("triage_data"):
            Triage.objects.create(
                dossier_medical=dossier,
                enregistre_par=user,
                **sections_data["triage_data"],
            )

        # Historique Médical
        if sections_data.get("historique_medical_data"):
            HistoriqueMedical.objects.create(
                dossier_medical=dossier,
                enregistre_par=user,
                **sections_data["historique_medical_data"],
            )

        # Historique Maladie Actuelle
        if sections_data.get("historique_maladie_actuelle_data"):
            HistoriqueMaladieActuelle.objects.create(
                dossier_medical=dossier,
                enregistre_par=user,
                **sections_data["historique_maladie_actuelle_data"],
            )

        # Blessures
        if sections_data.get("blessures_data"):
            self._create_blessures(dossier, sections_data["blessures_data"], user)

        # Interventions Médicaments/Liquides
        if sections_data.get("interventions_urgences_medicaments_liquide_data"):
            self._create_interventions_medicaments(
                dossier,
                sections_data["interventions_urgences_medicaments_liquide_data"],
                user,
            )

        # Interventions Procédures
        if sections_data.get("interventions_urgences_procedures_data"):
            self._create_interventions_procedures(
                dossier, sections_data["interventions_urgences_procedures_data"], user
            )

        # Interventions Tests Diagnostiques
        if sections_data.get("interventions_urgences_tests_diagnostiques_data"):
            self._create_interventions_tests(
                dossier,
                sections_data["interventions_urgences_tests_diagnostiques_data"],
                user,
            )

        # Disposition Unité Urgence
        if sections_data.get("disposition_unite_urgence_data"):
            DispositionUniteUrgence.objects.create(
                dossier_medical=dossier,
                enregistre_par=user,
                **sections_data["disposition_unite_urgence_data"],
            )

    def _create_information_variant_patient(self, dossier, data, user):
        """Crée la section Information Variant Patient avec géolocalisation."""
        geolocalisation_data = data.pop("geolocalisation", None)

        if geolocalisation_data:
            geolocalisation = Geolocalisation.objects.create(**geolocalisation_data)
            data["geolocalisation"] = geolocalisation

        InformationVariantPatient.objects.create(
            dossier_medical=dossier, enregistre_par=user, **data
        )

    def _create_blessures(self, dossier, data, user):
        """Crée la section Blessures avec ses détails."""
        details_data = data.pop("details", [])

        blessures = Blessures.objects.create(
            dossier_medical=dossier, enregistre_par=user, **data
        )

        for detail_data in details_data:
            conditions_ids = detail_data.pop("conditions", [])
            detail = BlessureDetail.objects.create(
                blessures_record=blessures, **detail_data
            )
            if conditions_ids:
                detail.conditions.set(conditions_ids)

    def _create_interventions_medicaments(self, dossier, data, user):
        """Crée la section Interventions Médicaments/Liquides."""
        if data.get("medicaments_liquide_administres") and not data.get(
            "medicaments_liquide_types"
        ):
            raise serializers.ValidationError(
                "Au moins un type de médicament doit être sélectionné."
            )
        types_ids = data.pop("medicaments_liquide_types", [])

        intervention = InterventionsUrgencesMedicamentsLiquide.objects.create(
            dossier_medical=dossier, enregistre_par=user, **data
        )

        if types_ids:
            intervention.medicaments_liquide_types.set(types_ids)

    def _create_interventions_procedures(self, dossier, data, user):
        """Crée la section Interventions Procédures."""
        types_ids = data.pop("procedures_types", [])

        intervention = InterventionsUrgencesProcedures.objects.create(
            dossier_medical=dossier, enregistre_par=user, **data
        )

        if types_ids:
            intervention.procedures_types.set(types_ids)

    def _create_interventions_tests(self, dossier, data, user):
        """Crée la section Interventions Tests Diagnostiques."""
        types_ids = data.pop("tests_diagnostiques_types", [])

        intervention = InterventionsUrgencesTestsDiagnostiques.objects.create(
            dossier_medical=dossier, enregistre_par=user, **data
        )

        if types_ids:
            intervention.tests_diagnostiques_types.set(types_ids)

    def _update_sections(self, dossier, sections_data):
        """Met à jour ou crée les sections existantes."""
        user = self.context.get("request").user if self.context.get("request") else None

        for section_key, section_data in sections_data.items():
            if not section_data:
                continue

            section_name = section_key.replace("_data", "")

            if section_name == "information_variant_patient":
                info_section = dossier.informationvariantpatient_sections.first()
                if info_section:
                    # Gestion spéciale pour la géolocalisation
                    geolocalisation_data = section_data.pop("geolocalisation", None)

                    # Mise à jour des champs simples
                    for key, value in section_data.items():
                        setattr(info_section, key, value)

                    # Gestion de la géolocalisation
                    if geolocalisation_data:
                        if info_section.geolocalisation:
                            # Mise à jour de la géolocalisation existante
                            for geo_key, geo_value in geolocalisation_data.items():
                                setattr(
                                    info_section.geolocalisation, geo_key, geo_value
                                )
                            info_section.geolocalisation.save()
                        else:
                            # Création d'une nouvelle géolocalisation
                            geolocalisation = Geolocalisation.objects.create(
                                **geolocalisation_data
                            )
                            info_section.geolocalisation = geolocalisation

                    info_section.save()
                else:
                    # Création
                    self._create_information_variant_patient(
                        dossier, section_data, user
                    )

            elif section_name == "signes_vitaux":
                signes_vitaux_section = dossier.signesvitaux_sections.first()
                if signes_vitaux_section:
                    # Mise à jour
                    for key, value in section_data.items():
                        setattr(signes_vitaux_section, key, value)
                    signes_vitaux_section.save()
                else:
                    # Création
                    SignesVitaux.objects.create(
                        dossier_medical=dossier,
                        enregistre_par=user,
                        **section_data,
                    )

            elif section_name == "evaluation_abcde":
                evaluation_section = dossier.evaluationabcde_sections.first()
                if evaluation_section:
                    # Mise à jour
                    for key, value in section_data.items():
                        setattr(evaluation_section, key, value)
                    evaluation_section.save()
                else:
                    # Création
                    EvaluationABCDE.objects.create(
                        dossier_medical=dossier,
                        enregistre_par=user,
                        **section_data,
                    )

            elif section_name == "triage":
                triage_section = dossier.triage_sections.first()
                if triage_section:
                    # Mise à jour
                    for key, value in section_data.items():
                        setattr(triage_section, key, value)
                    triage_section.save()
                else:
                    # Création
                    Triage.objects.create(
                        dossier_medical=dossier,
                        enregistre_par=user,
                        **section_data,
                    )

            elif section_name == "historique_medical":
                historique_section = dossier.historiquemedical_sections.first()
                if historique_section:
                    # Mise à jour
                    for key, value in section_data.items():
                        setattr(historique_section, key, value)
                    historique_section.save()
                else:
                    # Création
                    HistoriqueMedical.objects.create(
                        dossier_medical=dossier,
                        enregistre_par=user,
                        **section_data,
                    )

            elif section_name == "historique_maladie_actuelle":
                historique_hma_section = (
                    dossier.historiquemaladieactuelle_sections.first()
                )
                if historique_hma_section:
                    # Mise à jour
                    for key, value in section_data.items():
                        setattr(historique_hma_section, key, value)
                    historique_hma_section.save()
                else:
                    # Création
                    HistoriqueMaladieActuelle.objects.create(
                        dossier_medical=dossier,
                        enregistre_par=user,
                        **section_data,
                    )

            elif section_name == "blessures":
                blessures_section = dossier.blessures_sections.first()
                if blessures_section:
                    # Gestion spéciale pour les détails (relation)
                    details_data = section_data.pop("details", [])

                    # Mise à jour des champs simples
                    for key, value in section_data.items():
                        setattr(blessures_section, key, value)
                    blessures_section.save()

                    # Gestion des détails de blessures
                    if details_data:
                        # Supprimer les anciens détails et créer les nouveaux
                        blessures_section.details.all().delete()
                        for detail_data in details_data:
                            conditions_ids = detail_data.pop("conditions", [])
                            detail = BlessureDetail.objects.create(
                                blessures_record=blessures_section, **detail_data
                            )
                            if conditions_ids:
                                detail.conditions.set(conditions_ids)
                else:
                    # Création
                    self._create_blessures(dossier, section_data, user)

            elif section_name == "interventions_urgences_medicaments_liquide":
                interventions_medicaments_section = (
                    dossier.interventionsurgencesmedicamentsliquide_sections.first()
                )
                if interventions_medicaments_section:
                    # Gestion spéciale pour les relations ManyToMany
                    types_ids = section_data.pop("medicaments_liquide_types", [])

                    # Mise à jour des champs simples
                    for key, value in section_data.items():
                        setattr(interventions_medicaments_section, key, value)
                    interventions_medicaments_section.save()

                    # Mise à jour de la relation ManyToMany
                    if types_ids:
                        interventions_medicaments_section.medicaments_liquide_types.set(
                            types_ids
                        )
                else:
                    # Création
                    self._create_interventions_medicaments(dossier, section_data, user)

            elif section_name == "interventions_urgences_procedures":
                interventions_procedures_section = (
                    dossier.interventionsurgencesprocedures_sections.first()
                )
                if interventions_procedures_section:
                    # Gestion spéciale pour les relations ManyToMany
                    types_ids = section_data.pop("procedures_types", [])

                    # Mise à jour des champs simples
                    for key, value in section_data.items():
                        setattr(interventions_procedures_section, key, value)
                    interventions_procedures_section.save()

                    # Mise à jour de la relation ManyToMany
                    if types_ids:
                        interventions_procedures_section.procedures_types.set(types_ids)
                else:
                    # Création
                    self._create_interventions_procedures(dossier, section_data, user)

            elif section_name == "interventions_urgences_tests_diagnostiques":
                interventions_tests_section = (
                    dossier.interventionsurgencestestsdiagnostiques_sections.first()
                )
                if interventions_tests_section:
                    # Gestion spéciale pour les relations ManyToMany
                    types_ids = section_data.pop("tests_diagnostiques_types", [])

                    # Mise à jour des champs simples
                    for key, value in section_data.items():
                        setattr(interventions_tests_section, key, value)
                    interventions_tests_section.save()

                    # Mise à jour de la relation ManyToMany
                    if types_ids:
                        interventions_tests_section.tests_diagnostiques_types.set(
                            types_ids
                        )
                else:
                    # Création
                    self._create_interventions_tests(dossier, section_data, user)

            elif section_name == "disposition_unite_urgence":
                disposition_section = dossier.dispositionuniteurgence_sections.first()
                if disposition_section:
                    # Mise à jour
                    for key, value in section_data.items():
                        setattr(disposition_section, key, value)
                    disposition_section.save()
                else:
                    # Création
                    DispositionUniteUrgence.objects.create(
                        dossier_medical=dossier,
                        enregistre_par=user,
                        **section_data,
                    )
            else:
                raise serializers.ValidationError(
                    {section_name: f"Section '{section_name}' non gérée."}
                )
    def _update_patient_state(self, patient, suite_procedure):
        """Met à jour l'état du patient selon la suite de procédure."""
        if not patient or not suite_procedure:
            return

        if suite_procedure in ["hospitalisation", "transfert"]:
            patient.etat_de_la_personne = "malade"
        elif suite_procedure == "sortie":
            patient.etat_de_la_personne = "bonnesante"
        elif suite_procedure == "deces":
            patient.etat_de_la_personne = "mort"

        patient.save()
        
    @transaction.atomic
    def create(self, validated_data):
        sections_data = {
            f: validated_data.pop(f, {}) for f in self.fields if f.endswith("_data")
        }
        dossier = DossierMedical.objects.create(**validated_data)
        self._create_sections(dossier, sections_data)

        self._update_patient_state(dossier.patient, dossier.suite_procedure)

        return dossier


    @transaction.atomic
    def update(self, instance, validated_data):
        sections_data = {
            f: validated_data.pop(f, {}) for f in self.fields if f.endswith("_data")
        }
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._update_sections(instance, sections_data)

        self._update_patient_state(instance.patient, instance.suite_procedure)

        return instance


# ==================== SERIALIZER POUR LES AUTORISATIONS ====================


class AutorisationAccesDossierSerializer(serializers.ModelSerializer):
    dossier_numero = serializers.CharField(
        source="dossier.numero_dossier", read_only=True
    )
    hospital_demandeur_nom = serializers.CharField(
        source="hospital_demandeur.name", read_only=True
    )
    service_demandeur_nom = serializers.CharField(
        source="service_demandeur.name", read_only=True
    )
    hospital_proprietaire_nom = serializers.CharField(
        source="hospital_proprietaire.name", read_only=True
    )
    demandeur_nom = serializers.SerializerMethodField()

    class Meta:
        model = AutorisationAccesDossier
        fields = [
            "id",
            "dossier",
            "dossier_numero",
            "hospital_demandeur",
            "hospital_demandeur_nom",
            "service_demandeur",
            "service_demandeur_nom",
            "hospital_proprietaire",
            "hospital_proprietaire_nom",
            "demandeur",
            "demandeur_nom",
            "approbateur",
            "statut",
            "date_demande",
            "date_reponse",
            "date_expiration",
            "motif_demande",
            "motif_refus",
        ]
        read_only_fields = ["date_demande", "date_reponse", "hospital_proprietaire"]

    def get_demandeur_nom(self, obj):
        if obj.demandeur:
            return f"{obj.demandeur.first_name} {obj.demandeur.last_name}"
        return None
