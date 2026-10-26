from django.contrib import admin
from .models import TypeArticle, Fournisseur, Article, MouvementStock, MouvementArticle


@admin.register(TypeArticle)
class TypeArticleAdmin(admin.ModelAdmin):
    list_display = ("nom", "code", "description")
    search_fields = ("nom", "code")
    ordering = ("nom",)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("nom", "contact", "adresse")
    search_fields = ("nom", "contact")
    ordering = ("nom",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "nom", "type_article", "quantite_stock", "unite",
        "seuil_alerte", "seuil_critique", "prix_unitaire",
        "fournisseur_principal", "emplacement"
    )
    search_fields = ("nom", "description", "numero_lot", "code_barre")
    list_filter = ("type_article", "fournisseur_principal")
    ordering = ("nom",)
    list_editable = ("quantite_stock", "prix_unitaire")
    list_per_page = 20


class MouvementArticleInline(admin.TabularInline):
    model = MouvementArticle
    extra = 1
    autocomplete_fields = ["article"]


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = (
        "numero_mouvement", "type_mouvement", "type_beneficiaire",
        "beneficiaire", "date_mouvement", "montant_total"
    )
    search_fields = ("numero_mouvement", "beneficiaire", "commentaire")
    list_filter = ("type_mouvement", "type_beneficiaire", "date_mouvement")
    ordering = ("-date_mouvement",)
    inlines = [MouvementArticleInline]
    readonly_fields = ("numero_mouvement", "montant_total", "date_mouvement")