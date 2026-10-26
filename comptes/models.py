from django.db import models
from hospital.models import Hospital
from service.models import Service
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.core.exceptions import ValidationError
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(
        self,
        first_name,
        last_name,
        email,
        password=None,
        user_type="simple_user",
        hospital=None,
        service=None,
        phone_number=None,
        address=None,
        fonction=None,
        matricule_professionnel=None,
        profile_picture=None,
        biographie=None,
        is_active=False,
        is_staff=True,
        is_superuser=False,
    ):
        if not email:
            raise ValueError("L'email est obligatoire.")
        if not first_name:
            raise ValueError("Le prénom est obligatoire.")
        if not last_name:
            raise ValueError("Le nom est obligatoire.")
        if not hospital and user_type != "super_admin":
            raise ValueError(
                "Tous les utilisateurs (sauf les super admins) doivent être associés à un hôpital."
            )
        if not service and user_type != "super_admin":
            raise ValueError(
                "Tous les utilisateurs (sauf les super admins) doivent être associés à un service."
            )

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            hospital=hospital,
            service = service,
            profile_picture=profile_picture,
            phone_number=phone_number,
            address=address,
            fonction=fonction,
            biographie=biographie,
            matricule_professionnel=matricule_professionnel,
        )

        # Ici on hash correctement le mot de passe
        user.set_password(password)

        if user_type == "super_admin":
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
        elif user_type == "admin":
            user.is_staff = True
            user.is_active = is_active

        user.save(using=self._db)
        user.assign_permissions()
        return user

    def create_superuser(self, first_name, last_name, email, password, hospital=None, service=None):
        return self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            user_type="super_admin",
            hospital=hospital,
            service= service,
            is_active=True,
        )


class CustomUser(AbstractUser):
    SIMPLE_USER = "simple_user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

    USER_TYPE_CHOICES = (
        (SIMPLE_USER, "Utilisateur simple"),
        (ADMIN, "Admin"),
        (SUPER_ADMIN, "Super Admin"),
    )

    username = None
    email = models.EmailField(verbose_name="Email", unique=True)
    hospital = models.ForeignKey(Hospital,on_delete=models.CASCADE,null=True,blank=True,related_name="personnel",)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name="membre")
    first_name = models.CharField(verbose_name="Prénom", max_length=255)
    last_name = models.CharField(verbose_name="Nom", max_length=255)
    phone_number = models.CharField(
        verbose_name="Téléphone", max_length=20, blank=True, null=True
    )
    biographie = models.TextField(verbose_name="Biographie", blank=True, null=True)
    status = models.CharField(
        verbose_name="Statut",
        max_length=255,
        choices=[
            ("new", "Nouveau"),
            ("approved", "Approuvé"),
            ("rejected", "Rejeté"),
            ("blocked", "Bloqué"),
        ],
        default="new",
        blank=True,
        null=True,
    )
    address = models.CharField(
        verbose_name="Adresse", max_length=255, blank=True, null=True
    )
    fonction = models.CharField(
        verbose_name="Fonction", max_length=255, blank=True, null=True
    )
    matricule_professionnel = models.CharField(
        verbose_name="Matricule Professionnel", max_length=255, blank=True, null=True
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default=SIMPLE_USER
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        hospital_name = self.hospital.name if self.hospital else "Aucun hôpital"
        return f"{self.email} ({self.get_user_type_display()}, {hospital_name})"

    def clean(self):
        if not self.hospital and self.user_type != self.SUPER_ADMIN:
            raise ValidationError(
                "Tous les utilisateurs (sauf les super admins) doivent être rattachés à un hôpital."
            )
        super().clean()

    def save(self, *args, **kwargs):
        if self.user_type == self.SUPER_ADMIN:
            self.is_superuser = True
            self.is_staff = True
            self.is_active = True
        elif self.user_type == self.ADMIN:
            self.is_superuser = False
            self.is_staff = True
        else:
            self.is_superuser = False
            self.is_staff = False

        super().save(*args, **kwargs)
        self.assign_permissions()

    def assign_permissions(self):
        all_permissions = Permission.objects.all()

        forbidden_permissions = set()
        if self.user_type == self.SIMPLE_USER:
            forbidden_permissions = {
                "add_customuser",
                "delete_customuser",
                "add_hospital",
                "change_hospital",
                "delete_hospital",
            }
        elif self.user_type == self.ADMIN:
            forbidden_permissions = {
                "add_hospital",
                "delete_hospital",
                "change_hospital",
            }

        allowed_permissions = [
            perm
            for perm in all_permissions
            if perm.codename not in forbidden_permissions
        ]
        self.user_permissions.set(allowed_permissions)

    @property
    def is_admin(self):
        return self.user_type in [self.ADMIN, self.SUPER_ADMIN]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Education(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="education", on_delete=models.CASCADE
    )
    diplome = models.CharField(max_length=200)
    etablissement = models.CharField(max_length=200)
    annee = models.CharField(max_length=4)

    class Meta:
        ordering = ["-id"]


class Certification(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="certifications", on_delete=models.CASCADE
    )
    certification = models.CharField(max_length=255)

    class Meta:
        ordering = ["-id"]


class Specialite(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="specialites", on_delete=models.CASCADE
    )
    specialite = models.CharField(max_length=255)

    class Meta:
        ordering = ["-id"]


def jours_par_defaut():
    return ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]


class Horaire(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="horaires", on_delete=models.CASCADE
    )
    debut = models.TimeField(default="00:00:00")
    fin = models.TimeField(default="00:00:00")
    jours = models.JSONField(default=jours_par_defaut)


class Competence(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="competences", on_delete=models.CASCADE
    )
    nom = models.CharField(max_length=200)
    niveau = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["-id"]


class Statistique(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="statistiques", on_delete=models.CASCADE
    )
    patients = models.IntegerField(default=0)
    experience = models.IntegerField(default=0)
    consultations = models.IntegerField(default=0)


class Blocage(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="blocage", on_delete=models.CASCADE
    )
    raison = models.CharField(max_length=200)
    date = models.DateTimeField(blank=True, null=True)
    par = models.CharField(max_length=200)
    note = models.TextField()
