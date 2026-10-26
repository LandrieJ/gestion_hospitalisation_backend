from rest_framework import serializers
from .models import TypeArticle, Fournisseur, Article, MouvementStock, MouvementArticle


# -------- TYPE D'ARTICLE --------
class TypeArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeArticle
        fields = "__all__"


# -------- FOURNISSEUR --------
class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = "__all__"


# -------- ARTICLE --------
class ArticleSerializer(serializers.ModelSerializer):
    type_article = TypeArticleSerializer(read_only=True)
    type_article_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeArticle.objects.all(), source="type_article", write_only=True
    )

    fournisseur_principal = FournisseurSerializer(read_only=True)
    fournisseur_principal_id = serializers.PrimaryKeyRelatedField(
        queryset=Fournisseur.objects.all(),
        source="fournisseur_principal",
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "nom",
            "hospital",
            "type_article",
            "type_article_id",
            "description",
            "quantite_stock",
            "unite",
            "seuil_alerte",
            "seuil_critique",
            "code_barre",
            "numero_lot",
            "date_expiration",
            "prix_unitaire",
            "fournisseur_principal",
            "fournisseur_principal_id",
            "emplacement",
        ]


# -------- MOUVEMENT ARTICLE (détail d’un mouvement) --------
class MouvementArticleSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), source="article", write_only=True
    )

    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = MouvementArticle
        fields = [
            "id",
            "article",
            "article_id",
            "quantite",
            "prix_unitaire",
            "sous_total",
        ]

    def get_sous_total(self, obj):
        return obj.quantite * obj.prix_unitaire


# -------- MOUVEMENT STOCK --------
class MouvementStockSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()
    montant_total = serializers.ReadOnlyField()
    articles = MouvementArticleSerializer(many=True)

    class Meta:
        model = MouvementStock
        fields = [
            "id",
            "numero_mouvement",
            "type_beneficiaire",
            "beneficiaire",
            "contact",
            "date_mouvement",
            "type_mouvement",
            "commentaire",
            "utilisateur",
            "utilisateur_nom",
            "montant_total",
            "articles",
        ]
        read_only_fields = ["numero_mouvement", "date_mouvement", "montant_total"]

    def get_utilisateur_nom(self, obj):
        if obj.utilisateur:
            return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}".strip()
        return None

    def create(self, validated_data):
        articles_data = validated_data.pop("articles", [])
        mouvement = MouvementStock.objects.create(**validated_data)

        for item in articles_data:
            MouvementArticle.objects.create(mouvement=mouvement, **item)

        return mouvement

    def update(self, instance, validated_data):
        articles_data = validated_data.pop("articles", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if articles_data:
            instance.articles.all().delete()
            for item in articles_data:
                MouvementArticle.objects.create(mouvement=instance, **item)

        return instance
