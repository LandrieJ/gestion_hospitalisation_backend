from django.db import models
from hospital.models import Hospital
from django.dispatch import receiver
from django.db.models.signals import post_save

class ServiceChoices(models.TextChoices):
    URGENCES = "urgences", "Urgences"
    TRAUMATOLOGIE= "traumatologie", "Traumatologie"
    CARDIOLOGIE= "cardiologie", "Cardiologie"
    NEUROLOGIE= "neurologie", "Neurologie"
    PEDIATRIE= "pediatrie", "Pédiatrie"
    CHIRURGIE= "chirurgie", "Chirurgie"
    GYNECOLOGIE= "gynecologie", "Gynécologie & Obstétrique"
    ONCOLOGIE= "oncologie", "Oncologie"
    REANIMATION= "reanimation", "Réanimation"
    IMAGERIE= "imagerie", "Imagerie médicale"
    LABORATOIRE= "laboratoire", "Laboratoire"
    LOGISTIQUE= "logistique", "Logistique"
    ADMINISTRATION= "administration", "Administration"


class ServiceCodeChoises(models.TextChoices):
    URGENCES = "urgences", "URA"
    TRAUMATOLOGIE = "traumatologie", "TRA"
    CARDIOLOGIE = "cardiologie", "CAR"
    NEUROLOGIE = "neurologie", "NEU"
    PEDIATRIE = "pediatrie", "PED"
    CHIRURGIE = "chirurgie", "CHI"
    GYNECOLOGIE = "gynecologie", "GYN"
    ONCOLOGIE = "oncologie", "ONC"
    REANIMATION = "reanimation", "REA"
    IMAGERIE = "imagerie", "IMA"
    LABORATOIRE = "laboratoire", "LAB"
    LOGISTIQUE = "logistique", "LOG"
    ADMINISTRATION = "administration", "ADM"

class Service(models.Model):
    name = models.CharField(
        max_length=255,
        choices=ServiceChoices.choices
    )
    code = models.CharField(max_length=3, editable=False)
    nombre_chambre = models.IntegerField(default=2)
    nombre_lits_par_chambre = models.IntegerField(default=3)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="services")
    
    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['hospital', 'name'], name='unique_hospital_service')
        ]
        
    def save(self, *args, **kwargs):
        # self.code = ServiceCodeChoises.get(self.name, "DEF")
        if self.name:
            self.code = ServiceCodeChoises[self.name.upper()].label
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.hospital.name}"

    
    
class Bed(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="beds", null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        unique_together = ("service", "code")

    def __str__(self):
        return f"{self.code} ({'Occupé' if self.is_occupied else 'Libre'})"


@receiver(post_save, sender=Service)
def create_or_update_beds_for_service(sender, instance, created, **kwargs):
    chambres = instance.nombre_chambre or 2
    lits = instance.nombre_lits_par_chambre or 3

    expected_codes = [
        f"C{c}-L{l}" for c in range(1, chambres + 1) for l in range(1, lits + 1)
    ]

    existing_beds = instance.beds.all()
    existing_codes = set(existing_beds.values_list("code", flat=True))

    for bed in existing_beds:
        if bed.code not in expected_codes:
            bed.delete()

    for code in expected_codes:
        if code not in existing_codes:
            Bed.objects.create(service=instance, code=code)