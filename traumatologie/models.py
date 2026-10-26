from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


from patient.models import Patient
from comptes.models import CustomUser
from hospital.models import Hospital
from service.models import Service, Bed


class ProcedureType(models.Model):
    nom = models.CharField(
        max_length=100, unique=True, verbose_name="Nom de la procédure"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Type de Procédure"
        verbose_name_plural = "Types de Procédures"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class DiagnosticTestType(models.Model):
    nom = models.CharField(
        max_length=100, unique=True, verbose_name="Nom du test diagnostique"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Type de Test Diagnostique"
        verbose_name_plural = "Types de Tests Diagnostiques"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class MedicamentType(models.Model):
    """
    Modèle pour définir les différents types de médicaments.
    """

    nom_medicament = models.CharField(
        max_length=100, unique=True, verbose_name="Nom du médicament"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    dosage_standard = models.CharField(max_length=50, blank=True, null=True)
    unite_mesure = models.CharField(max_length=20, blank=True, null=True)
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Type de Médicament"
        verbose_name_plural = "Types de Médicaments"
        ordering = ["nom_medicament"]

    def __str__(self):
        return self.nom_medicament


class LocalisationType(models.Model):
    nom = models.CharField(
        max_length=50, unique=True, verbose_name="Nom de la localisation"
    )
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Type de Localisation Anatomique"
        verbose_name_plural = "Types de Localisations Anatomiques"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class ConditionType(models.Model):
    nom = models.CharField(
        max_length=50, unique=True, verbose_name="Nom de la condition"
    )
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Type de Condition"
        verbose_name_plural = "Types de Conditions"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Geolocalisation(models.Model):
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Géolocalisation"
        verbose_name_plural = "Géolocalisations"

    def __str__(self):
        return (
            f"({self.latitude}, {self.longitude})"
            if self.latitude and self.longitude
            else self.description or "Localisation"
        )


class DossierMedical(models.Model):
    """
    Modèle central pour gérer les dossiers médicaux.
    Chaque dossier correspond à une visite unique d'un patient dans un hôpital.
    """

    class StatutDossier(models.TextChoices):
        OUVERT = "ouvert", "Ouvert"
        EN_COURS = "en_cours", "En cours de traitement"
        FERME = "ferme", "Fermé"
        ARCHIVE = "archive", "Archivé"

    # Relations principales
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="dossiers_medicaux",
        verbose_name="Patient",
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="dossiers_medicaux",
        verbose_name="Hôpital",
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="dossiers_medicaux", verbose_name="Service")
    enregistrator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="dossiers_enregistres",
        verbose_name="Enregistreur",
    )

    # Informations du dossier
    numero_dossier = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de dossier",
        help_text="Généré automatiquement si non fourni",
    )
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True, verbose_name="Dernière modification"
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutDossier.choices,
        default=StatutDossier.OUVERT,
        verbose_name="Statut du dossier",
    )
    suite_procedure = models.CharField(max_length=50, default="domicile", verbose_name="Suite de procédure",)

    date_admission = models.DateTimeField(
        null=True, blank=True, verbose_name="Date et heure d'admission"
    )
    date_sortie = models.DateTimeField(
        null=True, blank=True, verbose_name="Date et heure de sortie"
    )

    # Contrôle d'accès
    dossier_prive = models.BooleanField(default=True, verbose_name="Dossier privé")
    hopitaux_autorises = models.ManyToManyField(
        Hospital,
        through="AutorisationAccesDossier",
        through_fields=("dossier", "hospital_demandeur"),
        related_name="dossiers_autorises",
        blank=True,
        verbose_name="Hôpitaux autorisés",
    )

    # Informations complémentaires
    motif_consultation = models.TextField(
        blank=True, null=True, verbose_name="Motif de consultation"
    )
    commentaires_generaux = models.TextField(
        blank=True, null=True, verbose_name="Commentaires généraux"
    )

    class Meta:
        verbose_name = "Dossier Médical"
        verbose_name_plural = "Dossiers Médicaux"
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["patient", "hospital"]),
            models.Index(fields=["date_admission"]),
            models.Index(fields=["numero_dossier"]),
        ]

    def save(self, *args, **kwargs):
        # Génération automatique du numéro de dossier
        if not self.numero_dossier:
            year = timezone.now().year
            hospital_code = (
                self.hospital.code if hasattr(self.hospital, "code") else "H"
            )
            count = (
                DossierMedical.objects.filter(
                    hospital=self.hospital, date_creation__year=year
                ).count()
                + 1
            )
            self.numero_dossier = f"{hospital_code}-{year}-{count:06d}"

        super().save(*args, **kwargs)

    def clean(self):
        # Validation : l'enregistreur doit travailler dans l'hôpital du dossier
        if self.enregistrator and self.hospital:
            if (
                hasattr(self.enregistrator, "hospital")
                and self.enregistrator.hospital != self.hospital
            ):
                raise ValidationError(
                    "L'enregistreur doit travailler dans l'hôpital où le dossier est créé."
                )

    def __str__(self):
        return f"Dossier {self.numero_dossier} - {self.patient} ({self.hospital})"

    @property
    def duree_sejour(self):
        """Calcule la durée du séjour en heures."""
        if self.date_sortie:
            return (self.date_sortie - self.date_admission).total_seconds() / 3600
        return None

    @property
    def est_en_cours(self):
        """Vérifie si le dossier est encore ouvert."""
        return self.statut in [self.StatutDossier.OUVERT, self.StatutDossier.EN_COURS]


class AutorisationAccesDossier(models.Model):
    """
    Modèle pour gérer les autorisations d'accès aux dossiers entre hôpitaux.
    """

    class StatutDemande(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        APPROUVEE = "approuvee", "Approuvée"
        REFUSEE = "refusee", "Refusée"
        EXPIREE = "expiree", "Expirée"

    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)
    hospital_demandeur = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="demandes_acces_emises"
    )
    service_demandeur = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="demandes_acces_emises"
    )
    hospital_proprietaire = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="demandes_acces_recues"
    )

    demandeur = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="demandes_acces_emises"
    )
    approbateur = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes_acces_approuvees",
    )

    statut = models.CharField(
        max_length=20, choices=StatutDemande.choices, default=StatutDemande.EN_ATTENTE
    )

    date_demande = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(null=True, blank=True)
    date_expiration = models.DateTimeField(null=True, blank=True)

    motif_demande = models.TextField(verbose_name="Motif de la demande")
    motif_refus = models.TextField(blank=True, null=True, verbose_name="Motif de refus")

    class Meta:
        verbose_name = "Autorisation d'Accès au Dossier"
        verbose_name_plural = "Autorisations d'Accès aux Dossiers"
        unique_together = ("dossier", "hospital_demandeur")

    def __str__(self):
        return f"Demande {self.hospital_demandeur} → {self.hospital_proprietaire} ({self.statut})"


class SectionDossier(models.Model):
    """
    Classe abstraite de base pour toutes les sections d'un dossier médical.
    """

    dossier_medical = models.ForeignKey(
        DossierMedical,
        on_delete=models.CASCADE,
        related_name="%(class)s_sections",
        verbose_name="Dossier médical",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    enregistre_par = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_enregistres",
    )

    class Meta:
        abstract = True

    def clean(self):
        # Validation : l'enregistreur doit avoir accès au dossier
        if self.enregistre_par and self.dossier_medical:
            if (
                self.enregistre_par.hospital != self.dossier_medical.hospital
                and not self.dossier_medical.hopitaux_autorises.filter(
                    id=self.enregistre_par.hospital.id
                ).exists()
            ):
                raise ValidationError(
                    "Vous n'avez pas l'autorisation d'enregistrer des données dans ce dossier."
                )


class InformationVariantPatient(SectionDossier):
    class ModeArrivee(models.TextChoices):
        AMBULANCE = "ambulance", "Ambulance"
        PERSONNEL = "vehicule_personnel", "Véhicule personnel"
        HELICOPTERE = "helicoptere", "Hélicoptère"
        AUTRE = "autre", "Autre"

    class ClassificationProfession(models.TextChoices):
        MEDICALE = "medicale", "Médicale"
        JURIDIQUE = "juridique", "Juridique"
        TECHNIQUE = "technique", "Technique"
        AUTRE = "autre", "Autre"

    mode_arrivee = models.CharField(
        max_length=50, choices=ModeArrivee.choices, blank=True
    )
    autre_mode_arrivee = models.CharField(max_length=255, blank=True, null=True)
    nombre_frequentations_medicales = models.PositiveIntegerField(null=True, blank=True)
    classification_profession = models.CharField(
        max_length=50, choices=ClassificationProfession.choices, blank=True
    )

    profession_specifique = models.CharField(max_length=255, blank=True, null=True)
    domicile = models.CharField(max_length=255, blank=True, null=True)
    residence_secondaire = models.CharField(max_length=255, blank=True, null=True)
    lieu_accident = models.CharField(max_length=255, blank=True, null=True)
    geolocalisation = models.ForeignKey(
        Geolocalisation, on_delete=models.SET_NULL, blank=True, null=True
    )
    accident_de_masse = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Information Variant Patient"
        verbose_name_plural = "Informations Variants Patients"

    def __str__(self):
        return f"Informations variant - Dossier {self.dossier_medical.numero_dossier}"


class SignesVitaux(SectionDossier):
    class ModeAdministrationOxygene(models.TextChoices):
        AUCUNE = "aucune", "Aucune"
        MASQUE = "masque", "Masque à oxygène"
        CANULE = "canule", "Canule nasale"
        AUTRE = "autre", "Autre"

    signes_de_vie = models.BooleanField(default=True)
    pression_arterielle_systolique = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(300)])
    pression_arterielle_diastolique = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)], blank=True, null=True)
    frequence_cardiaque = models.PositiveIntegerField(blank=True, null=True)
    saturation_oxygene = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    administration_oxygene = models.CharField(
        max_length=50,
        choices=ModeAdministrationOxygene.choices,
        default=ModeAdministrationOxygene.AUCUNE,
        blank=True,
        null=True,
    )
    frequence_respiratoire = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Signes Vitaux"
        verbose_name_plural = "Signes Vitaux"

    def __str__(self):
        return f"Signes vitaux - Dossier {self.dossier_medical.numero_dossier}"


class EvaluationABCDE(SectionDossier):
    class EvdaChoices(models.TextChoices):
        ALERTE = "A", "A - Alerte"
        VERBAL = "V", "V - Réponse verbale"
        DOULEUR = "D", "D - Réponse à la douleur"
        SANS_REPONSE = "U", "U - Sans réponse"

    class PupillesChoices(models.IntegerChoices):
        ZERO = 0, "0 - Aucune"
        UNE = 1, "1 - Une seule pupille"
        DEUX = 2, "2 - Les deux pupilles"

    evda_initiale = models.CharField(
        max_length=1, choices=EvdaChoices.choices, blank=True
    )

    score_glasgow_yeux = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)], null=True, blank=True
    )
    score_glasgow_verbal = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True
    )
    score_glasgow_motricite = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)], null=True, blank=True
    )

    score_glasgow_total = models.PositiveSmallIntegerField(null=True, blank=True)
    glasgow_qualifie = models.BooleanField(default=False)

    nombre_reaction_pupillaire = models.PositiveSmallIntegerField(
        choices=PupillesChoices.choices, null=True, blank=True
    )

    class Meta:
        verbose_name = "Évaluation ABCDE"
        verbose_name_plural = "Évaluations ABCDE"

    def save(self, *args, **kwargs):
        scores = [
            self.score_glasgow_yeux,
            self.score_glasgow_verbal,
            self.score_glasgow_motricite,
        ]
        if all(s is not None for s in scores):
            self.score_glasgow_total = sum(scores)
        else:
            self.score_glasgow_total = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Évaluation ABCDE - Dossier {self.dossier_medical.numero_dossier} - Glasgow: {self.score_glasgow_total or 'N/A'}"


class Triage(SectionDossier):
    class OutilTriageChoices(models.TextChoices):
        ESI = "ESI", "ESI (Emergency Severity Index)"
        CIMU = "CIMU", "CIMU (Classification Infirmière des Malades aux Urgences)"
        FRENCH = "FRENCH", "FRENCH"
        AUTRE = "autre", "Autre"

    triage_effectue = models.BooleanField(default=False)
    outil_triage = models.CharField(
        max_length=50, choices=OutilTriageChoices.choices, blank=True, null=True
    )
    autre_outil_triage = models.CharField(max_length=255, blank=True, null=True)
    autre_categorie_outil_triage = models.CharField(
        max_length=255, blank=True, null=True
    )

    class Meta:
        verbose_name = "Triage"
        verbose_name_plural = "Triages"

    def clean(self):
        super().clean()
        if not self.triage_effectue:
            if (
                self.outil_triage
                or self.autre_outil_triage
                or self.autre_categorie_outil_triage
            ):
                raise ValidationError(
                    "Les détails du triage ne peuvent être remplis si 'triage_effectue' est faux."
                )
        if (
            self.outil_triage != self.OutilTriageChoices.AUTRE
            and self.autre_outil_triage
        ):
            raise ValidationError(
                "Le champ 'autre_outil_triage' ne doit être rempli que si l'outil de triage est 'Autre'."
            )

    def __str__(self):
        if self.triage_effectue:
            return f"Triage - Dossier {self.dossier_medical.numero_dossier} avec {self.outil_triage}"
        return f"Aucun triage - Dossier {self.dossier_medical.numero_dossier}"


class HistoriqueMedical(SectionDossier):
    nombre_comorbidites = models.IntegerField(blank=True, null=True)
    patiente_enceinte = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Historique Médical"
        verbose_name_plural = "Historiques Médicaux"

    def __str__(self):
        return f"Historique médical - Dossier {self.dossier_medical.numero_dossier}"


class HistoriqueMaladieActuelle(SectionDossier):
    date_accident = models.DateField(blank=True, null=True)
    hma_lieu_accident = models.CharField(max_length=255, blank=True, null=True)
    autre_lieu_accident = models.CharField(max_length=255, blank=True, null=True)
    activite_lors_accident = models.CharField(max_length=255, blank=True, null=True)
    autre_activite_lors_accident = models.CharField(
        max_length=255, blank=True, null=True
    )
    mecanisme_accident = models.CharField(max_length=255, blank=True, null=True)
    autre_mecanisme_accident = models.CharField(max_length=255, blank=True, null=True)
    materiel_protection = models.CharField(max_length=255, blank=True, null=True)
    autre_materiel_protection = models.CharField(max_length=255, blank=True, null=True)
    mecanisme_supplementaire = models.BooleanField(default=False)
    protection_utilisee = models.BooleanField(default=False)
    intentionnel = models.BooleanField(default=False)
    soins_prehospitaliers = models.BooleanField(default=False)
    prise_en_charge_medical_lieu_accident_lors_transport = models.BooleanField(
        default=False
    )
    hma_autre_mode_arrivee = models.BooleanField(default=False)
    procedure_supplementaire = models.BooleanField(default=False)
    consommation_substance = models.CharField(max_length=255, blank=True, null=True)
    consommation_alcool = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Historique de la Maladie Actuelle"
        verbose_name_plural = "Historiques des Maladies Actuelles"

    def __str__(self):
        return f"HMA - Dossier {self.dossier_medical.numero_dossier}"


class Blessures(SectionDossier):
    checklist_trauma_utilisee = models.BooleanField(
        default=False, verbose_name="Checklist trauma utilisée"
    )
    blessure_supplementaire = models.BooleanField(
        default=False, verbose_name="Blessure(s) supplémentaire(s)"
    )

    class Meta:
        verbose_name = "Rapport de Blessures"
        verbose_name_plural = "Rapports de Blessures"

    def __str__(self):
        return f"Blessures - Dossier {self.dossier_medical.numero_dossier}"


class BlessureDetail(models.Model):
    blessures_record = models.ForeignKey(
        Blessures,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="Enregistrement de Blessures Parent",
    )
    localisation = models.ForeignKey(
        LocalisationType,
        on_delete=models.CASCADE,
        related_name="blessure_details",
        verbose_name="Localisation anatomique",
    )
    conditions = models.ManyToManyField(
        ConditionType,
        related_name="blessure_details",
        verbose_name="Conditions associées",
    )

    class Meta:
        verbose_name = "Détail de Blessure"
        verbose_name_plural = "Détails de Blessures"
        unique_together = (
            "blessures_record",
            "localisation",
        )

    def __str__(self):
        conditions_list = self.conditions.all().values_list("nom", flat=True)
        conditions_str = ", ".join(conditions_list)
        return (
            f"{self.localisation.nom} - {conditions_str}"
            if conditions_str
            else f"{self.localisation.nom} (sans conditions)"
        )


class InterventionsUrgencesMedicamentsLiquide(SectionDossier):
    medicaments_liquide_administres = models.BooleanField(default=False)
    medicaments_liquide_types = models.ManyToManyField(MedicamentType, blank=True)
    medicaments_liquide_autre = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Intervention - Médicaments/Liquides"
        verbose_name_plural = "Interventions - Médicaments/Liquides"

    def __str__(self):
        return f"Médicaments/Liquides - Dossier {self.dossier_medical.numero_dossier}"


class InterventionsUrgencesProcedures(SectionDossier):
    procedures = models.BooleanField(default=False)
    procedures_types = models.ManyToManyField(ProcedureType, blank=True)
    procedures_autre = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Intervention - Procédures"
        verbose_name_plural = "Interventions - Procédures"

    def __str__(self):
        return f"Procédures - Dossier {self.dossier_medical.numero_dossier}"


class InterventionsUrgencesTestsDiagnostiques(SectionDossier):
    tests_diagnostiques = models.BooleanField(default=False)
    tests_diagnostiques_types = models.ManyToManyField(DiagnosticTestType, blank=True)
    tests_diagnostiques_autre = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Intervention - Tests Diagnostiques"
        verbose_name_plural = "Interventions - Tests Diagnostiques"

    def __str__(self):
        return f"Tests Diagnostiques - Dossier {self.dossier_medical.numero_dossier}"


class DispositionUniteUrgence(SectionDossier):
    class SortieSuChoices(models.TextChoices):
        DOMICILE = "domicile", "Retour à domicile"
        HOSPITALISATION = "hospitalisation", "Hospitalisation"
        TRANSFERT = "transfert", "Transfert"
        DECES = "deces", "Décès"
        AUTRE = "autre", "Autre"


    sortie_su = models.CharField(max_length=255, choices=SortieSuChoices.choices, blank=True, null=True)
    heure_sortie_unite_urgence = models.TimeField(auto_now_add=True,)
    date_sortie_unite_urgence = models.DateField(auto_now_add=True)
    autre_sortie_su = models.CharField(max_length=255, blank=True, null=True)
    consignes_domicile = models.TextField(blank=True, null=True)
    accompagnant = models.CharField(max_length=255, blank=True, null=True)
    rdv_controle = models.DateField(blank=True, null=True)
    diagnostique_hospitalisation = models.TextField(blank=True, null=True)
    numero_chambre_lit = models.ForeignKey(Bed, on_delete=models.SET_NULL, blank=True, null=True)
    hopital_transfert = models.CharField(max_length=255, blank=True, null=True)
    autre_hopital = models.CharField(max_length=255, blank=True, null=True)
    service_transfert = models.CharField(max_length=255, blank=True, null=True)
    autre_service_transfert = models.CharField(max_length=255, blank=True, null=True)
    motif_transfert = models.CharField(max_length=255, blank=True, null=True)
    cause_deces = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Disposition Unité d'Urgence"
        verbose_name_plural = "Dispositions Unités d'Urgence"

    def __str__(self):
        return f"Disposition - Dossier {self.dossier_medical.numero_dossier}"
