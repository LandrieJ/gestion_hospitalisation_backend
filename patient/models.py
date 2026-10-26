from django.db import models
from comptes.models import Hospital, CustomUser

class Etat(models.TextChoices):
    BONNE_SANTE = 'bonnesante', 'En bonne santé'
    MALADE = 'malade', 'Malade'
    INCERTAIN = 'mort', 'Mort'

class Patient(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    cin_connu = models.BooleanField(default=False)
    cin_number = models.BigIntegerField(blank=True, null=True)
    age_connu = models.BooleanField(default=False)
    birth_date = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    etat_de_la_personne = models.CharField(max_length=255, choices=Etat.choices, default='bonnesante', blank=True, null=True)
    hospitals_actuel = models.ManyToManyField(Hospital, related_name='patients_actuels', blank=True)
    GENRE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
    ]
    genre = models.CharField(max_length=10, choices=GENRE_CHOICES)

    hospitals = models.ManyToManyField(Hospital, related_name='patients')
    registered_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_registered')
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
