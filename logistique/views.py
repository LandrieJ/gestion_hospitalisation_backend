from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .models import TypeArticle, Fournisseur, Article, MouvementStock, MouvementArticle
from .serializers import (
    TypeArticleSerializer, FournisseurSerializer,
    ArticleSerializer, MouvementStockSerializer
)


# -------- TYPE ARTICLE --------
class TypeArticleViewSet(viewsets.ModelViewSet):
    queryset = TypeArticle.objects.all().order_by("nom")
    serializer_class = TypeArticleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "code"]


# -------- FOURNISSEUR --------
class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all().order_by("nom")
    serializer_class = FournisseurSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "contact"]


# -------- ARTICLE --------
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related("type_article", "fournisseur_principal").all()
    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom", "description", "numero_lot", "code_barre"]
    ordering_fields = ["nom", "quantite_stock", "prix_unitaire"]
    ordering = ["nom"]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par hôpital
        user_hospital = getattr(self.request.user, "hospital", None)
        if user_hospital:
            queryset = queryset.filter(hospital=user_hospital)

        # Filtre par type_article
        type_id = self.request.query_params.get("type_article")
        if type_id:
            try:
                type_id = int(type_id)
                queryset = queryset.filter(type_article_id=type_id)
            except ValueError:
                pass

        # Filtre par stock_status
        stock_status = self.request.query_params.get("stock_status")
        if stock_status == "low":
            queryset = queryset.filter(
                quantite_stock__lte=models.F("seuil_alerte"),
                quantite_stock__gt=models.F("seuil_critique")  # optionnel pour éviter chevauchement
            )
        elif stock_status == "critical":
            queryset = queryset.filter(quantite_stock__lte=models.F("seuil_critique"))

        return queryset

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()
        mutable_data["hospital"] = request.user.hospital.id
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# -------- MOUVEMENT STOCK (Commandes) --------
class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.prefetch_related("articles__article").all().order_by("-date_mouvement")
    serializer_class = MouvementStockSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["numero_mouvement", "beneficiaire", "commentaire"]
    ordering_fields = ["date_mouvement", "montant_total"]
    ordering = ["-date_mouvement"]

    def perform_create(self, serializer):
        # Attribution de l’utilisateur connecté et génération auto d’un numéro
        last_id = MouvementStock.objects.count() + 1
        numero_mouvement = f"MVT-{timezone.now().strftime('%Y%m%d')}-{last_id:04d}"
        serializer.save(utilisateur=self.request.user, numero_mouvement=numero_mouvement)