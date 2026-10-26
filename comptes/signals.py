from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Horaire

@receiver(post_save, sender=CustomUser)
def creer_horaire_par_defaut(sender, instance, created, **kwargs):
    if created:
        Horaire.objects.create(user=instance)
