from django.db import models
from django.conf import settings
from comptes.models import Hospital

# --------- TYPE D'ARTICLE ---------
class TypeArticle(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.code})"


# --------- FOURNISSEUR ---------
class Fournisseur(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    contact = models.CharField(max_length=255, blank=True, null=True)  # téléphone ou email
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


# --------- ARTICLE ---------
class Article(models.Model):
    nom = models.CharField(max_length=255)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="articles")
    type_article = models.ForeignKey(TypeArticle, on_delete=models.PROTECT, related_name="articles")
    description = models.TextField(blank=True, null=True)

    quantite_stock = models.PositiveIntegerField(default=0)
    unite = models.CharField(max_length=50, default="unité")

    seuil_alerte = models.PositiveIntegerField(default=10)
    seuil_critique = models.PositiveIntegerField(default=5)

    code_barre = models.CharField(max_length=100, blank=True, null=True)
    numero_lot = models.CharField(max_length=100, blank=True, null=True)
    date_expiration = models.DateField(blank=True, null=True)

    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    fournisseur_principal = models.ForeignKey(
        Fournisseur, on_delete=models.SET_NULL, blank=True, null=True, related_name="articles"
    )
    emplacement = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nom


# --------- MOUVEMENT / COMMANDE ---------
class MouvementStock(models.Model):
    TYPE_BENEFICIAIRE_CHOICES = [
        ("famille", "Famille de patient"),
        ("personnel", "Personnel médical"),
        ("service", "Service/Département"),
    ]

    TYPE_MOUVEMENT_CHOICES = [
        ("vente", "Vente"),
        ("don", "Don/Aide sociale"),
        ("usage_medical", "Usage médical"),
        ("formation", "Formation"),
        ("maintenance", "Maintenance/Nettoyage"),
        ("administration", "Administration"),
    ]

    numero_mouvement = models.CharField(max_length=50, unique=True)
    type_beneficiaire = models.CharField(max_length=20, choices=TYPE_BENEFICIAIRE_CHOICES)
    beneficiaire = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True, null=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    type_mouvement = models.CharField(max_length=50, choices=TYPE_MOUVEMENT_CHOICES)
    commentaire = models.TextField(blank=True, null=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    @property
    def montant_total(self):
        return sum([item.quantite * item.prix_unitaire for item in self.articles.all()])

    def __str__(self):
        return f"{self.numero_mouvement} - {self.get_type_mouvement_display()}"


# --------- DETAIL D'UN MOUVEMENT ---------
class MouvementArticle(models.Model):
    mouvement = models.ForeignKey(MouvementStock, on_delete=models.CASCADE, related_name="articles")
    article = models.ForeignKey(Article, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.article.nom} x {self.quantite}"