from django.db import models
from django.conf import settings

class TypeChoix(models.TextChoices):
    REUNION = 'reunions', 'Réunions'
    CONFERENCE = 'conferences', 'Conférences'
    ATELIER = 'ateliers', 'Ateliers'
    INSPECTION = 'inspections', 'Inspections'
    FORMATION = 'formations', 'Formations'

class ServiceChoix(models.TextChoices):
    TRAUM = 'traumatologie', 'Traumatologie'
    LOGISTIQUE = 'logistique', 'Logistique'
    CARDIO = 'cardiologie', 'Cardiologie'
    PEDIATRIE = 'pediatrie', 'Pédiatrie'

class Evenement(models.Model):
    time = models.DateTimeField()
    event = models.TextField(max_length=255)
    type = models.CharField(max_length=255, choices=TypeChoix.choices)
    service = models.CharField(max_length=255, choices=ServiceChoix.choices)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.event

    class Meta:
        ordering = ['-time']