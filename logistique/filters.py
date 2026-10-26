# from datetime import timezone
# import django_filters
# from django.db.models import Q, F
# from .models import Article, Commande, HistoriqueMouvement


# class ArticleFilter(django_filters.FilterSet):
#     """Filtres pour les articles"""
    
#     nom = django_filters.CharFilter(lookup_expr='icontains')
#     type_article = django_filters.NumberFilter()
#     type_article_nom = django_filters.CharFilter(field_name='type_article__nom', lookup_expr='icontains')
#     fournisseur = django_filters.NumberFilter(field_name='fournisseur_principal')
#     fournisseur_nom = django_filters.CharFilter(field_name='fournisseur_principal__nom', lookup_expr='icontains')
    
#     # Filtres sur les quantités
#     quantite_stock_min = django_filters.NumberFilter(field_name='quantite_stock', lookup_expr='gte')
#     quantite_stock_max = django_filters.NumberFilter(field_name='quantite_stock', lookup_expr='lte')
    
#     # Filtres sur les prix
#     prix_min = django_filters.NumberFilter(field_name='prix_unitaire', lookup_expr='gte')
#     prix_max = django_filters.NumberFilter(field_name='prix_unitaire', lookup_expr='lte')
    
#     # Filtres sur les niveaux d'alerte
#     niveau_alerte = django_filters.ChoiceFilter(
#         choices=[
#             ('normal', 'Normal'),
#             ('alerte', 'Alerte'),
#             ('critique', 'Critique'),
#         ],
#         method='filter_niveau_alerte'
#     )
    
#     # Filtres sur les dates d'expiration
#     expire_avant = django_filters.DateFilter(field_name='date_expiration', lookup_expr='lte')
#     expire_apres = django_filters.DateFilter(field_name='date_expiration', lookup_expr='gte')
#     expire_dans = django_filters.NumberFilter(method='filter_expire_dans')
    
#     # Filtre pour les articles sans stock
#     sans_stock = django_filters.BooleanFilter(method='filter_sans_stock')
    
#     # Filtre pour les articles avec stock faible
#     stock_faible = django_filters.BooleanFilter(method='filter_stock_faible')
    
#     # Filtre par emplacement
#     emplacement = django_filters.CharFilter(lookup_expr='icontains')
    
#     class Meta:
#         model = Article
#         fields = [
#             'nom', 'type_article', 'type_article_nom', 'fournisseur', 'fournisseur_nom',
#             'quantite_stock_min', 'quantite_stock_max', 'prix_min', 'prix_max',
#             'niveau_alerte', 'expire_avant', 'expire_apres', 'expire_dans',
#             'sans_stock', 'stock_faible', 'emplacement', 'unite'
#         ]

#     def filter_niveau_alerte(self, queryset, name, value):
#         """Filtre par niveau d'alerte"""
#         if value == 'critique':
#             return queryset.filter(quantite_stock__lte=F('seuil_critique'))
#         elif value == 'alerte':
#             return queryset.filter(
#                 quantite_stock__lte=F('seuil_alerte'),
#                 quantite_stock__gt=F('seuil_critique')
#             )
#         elif value == 'normal':
#             return queryset.filter(quantite_stock__gt=F('seuil_alerte'))
#         return queryset
#     def filter_expire_dans(self, queryset, name, value):
#         """Filtre les articles qui expirent dans un certain nombre de jours"""
#         if value is not None:
#             return queryset.filter(date_expiration__lte=timezone.now() + timezone.timedelta(days=value))
#         return queryset
#     def filter_sans_stock(self, queryset, name, value):
#         """Filtre les articles sans stock"""
#         if value:
#             return queryset.filter(quantite_stock=0)
#         return queryset
#     def filter_stock_faible(self, queryset, name, value):
#         """Filtre les articles avec un stock faible"""
#         if value:
#             return queryset.filter(quantite_stock__lte=F('seuil_critique'))
#         return queryset
#     def filter_emplacement(self, queryset, name, value):
#         """Filtre les articles par emplacement"""
#         if value:
#             return queryset.filter(emplacement__icontains=value)
#         return queryset
#     def filter_fournisseur(self, queryset, name, value):
#         """Filtre les articles par fournisseur"""
#         if value:
#             return queryset.filter(fournisseur_principal__id=value)
#         return queryset
#     def filter_fournisseur_nom(self, queryset, name, value):
#         """Filtre les articles par nom de fournisseur"""
#         if value:
#             return queryset.filter(fournisseur_principal__nom__icontains=value)
#         return queryset
#     def filter_type_article(self, queryset, name, value):
#         """Filtre les articles par type d'article"""
#         if value:
#             return queryset.filter(type_article__id=value)
#         return queryset
#     def filter_type_article_nom(self, queryset, name, value):
#         """Filtre les articles par nom de type d'article"""
#         if value:
#             return queryset.filter(type_article__nom__icontains=value)
#         return queryset
#     def filter_nom(self, queryset, name, value):
#         """Filtre les articles par nom"""
#         if value:
#             return queryset.filter(nom__icontains=value)
#         return queryset
#     def filter_quantite_stock_min(self, queryset, name, value):
#         """Filtre les articles avec une quantité de stock minimale"""
#         if value is not None:
#             return queryset.filter(quantite_stock__gte=value)
#         return queryset
#     def filter_quantite_stock_max(self, queryset, name, value):
#         """Filtre les articles avec une quantité de stock maximale"""
#         if value is not None:
#             return queryset.filter(quantite_stock__lte=value)
#         return queryset
#     def filter_prix_min(self, queryset, name, value):
#         """Filtre les articles avec un prix unitaire minimum"""
#         if value is not None:
#             return queryset.filter(prix_unitaire__gte=value)
#         return queryset
#     def filter_prix_max(self, queryset, name, value):
#         """Filtre les articles avec un prix unitaire maximum"""
#         if value is not None:
#             return queryset.filter(prix_unitaire__lte=value)
#         return queryset
# class CommandeFilter(django_filters.FilterSet):
#     """Filtres pour les commandes"""
    
#     numero = django_filters.CharFilter(lookup_expr='icontains')
#     fournisseur = django_filters.NumberFilter(field_name='fournisseur')
#     fournisseur_nom = django_filters.CharFilter(field_name='fournisseur__nom', lookup_expr='icontains')
#     statut = django_filters.ChoiceFilter(
#         choices=Commande.STATUT_CHOICES,
#         method='filter_statut'
#     )
#     date_creation_min = django_filters.DateTimeFilter(field_name='date_creation', lookup_expr='gte')
#     date_creation_max = django_filters.DateTimeFilter(field_name='date_creation', lookup_expr='lte')
    
#     class Meta:
#         model = Commande
#         fields = ['numero', 'fournisseur', 'fournisseur_nom', 'statut', 'date_creation_min', 'date_creation_max']
    
#     def filter_statut(self, queryset, name, value):
#         """Filtre par statut de la commande"""
#         if value:
#             return queryset.filter(statut=value)
#         return queryset
#     def filter_fournisseur(self, queryset, name, value):
#         """Filtre les commandes par fournisseur"""
#         if value:
#             return queryset.filter(fournisseur__id=value)
#         return queryset
#     def filter_fournisseur_nom(self, queryset, name, value):
#         """Filtre les commandes par nom de fournisseur"""
#         if value:
#             return queryset.filter(fournisseur__nom__icontains=value)
#         return queryset
#     def filter_numero(self, queryset, name, value):
#         """Filtre les commandes par numéro"""
#         if value:
#             return queryset.filter(numero__icontains=value)
#         return queryset
#     def filter_date_creation_min(self, queryset, name, value):
#         """Filtre les commandes créées après une certaine date"""
#         if value is not None:
#             return queryset.filter(date_creation__gte=value)
#         return queryset
#     def filter_date_creation_max(self, queryset, name, value):
#         """Filtre les commandes créées avant une certaine date"""
#         if value is not None:
#             return queryset.filter(date_creation__lte=value)
#         return queryset
# class HistoriqueMouvementFilter(django_filters.FilterSet):
#     """Filtres pour les mouvements d'articles"""
    
#     article = django_filters.NumberFilter(field_name='article')
#     article_nom = django_filters.CharFilter(field_name='article__nom', lookup_expr='icontains')
#     type_mouvement = django_filters.ChoiceFilter(
#         choices=HistoriqueMouvement.TYPE_MOUVEMENT_CHOICES,
#         method='filter_type_mouvement'
#     )
#     date_min = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte')
#     date_max = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    
#     class Meta:
#         model = HistoriqueMouvement
#         fields = ['article', 'article_nom', 'type_mouvement', 'date_min', 'date_max']
    
#     def filter_type_mouvement(self, queryset, name, value):
#         """Filtre par type de mouvement"""
#         if value:
#             return queryset.filter(type_mouvement=value)
#         return queryset
#     def filter_article(self, queryset, name, value):
#         """Filtre les mouvements par article"""
#         if value:
#             return queryset.filter(article__id=value)
#         return queryset
#     def filter_article_nom(self, queryset, name, value):
#         """Filtre les mouvements par nom d'article"""
#         if value:
#             return queryset.filter(article__nom__icontains=value)
#         return queryset
#     def filter_date_min(self, queryset, name, value):
#         """Filtre les mouvements après une certaine date"""
#         if value is not None:
#             return queryset.filter(date__gte=value)
#         return queryset
#     def filter_date_max(self, queryset, name, value):
#         """Filtre les mouvements avant une certaine date"""
#         if value is not None:
#             return queryset.filter(date__lte=value)
#         return queryset
#     # URLs pour les listes filtrées
#     def filter_emplacement(self, queryset, name, value):
#         """Filtre les mouvements par emplacement"""
#         if value:
#             return queryset.filter(article__emplacement__icontains=value)
#         return queryset
#     def filter_fournisseur(self, queryset, name, value):
#         """Filtre les mouvements par fournisseur"""
#         if value:
#             return queryset.filter(article__fournisseur_principal__id=value)
#         return queryset
#     def filter_fournisseur_nom(self, queryset, name, value):
#         """Filtre les mouvements par nom de fournisseur"""
#         if value:
#             return queryset.filter(article__fournisseur_principal__nom__icontains=value)
#         return queryset
#     def filter_type_article(self, queryset, name, value):
#         """Filtre les mouvements par type d'article"""
#         if value:
#             return queryset.filter(article__type_article__id=value)
#         return queryset
#     def filter_type_article_nom(self, queryset, name, value):
#         """Filtre les mouvements par nom de type d'article"""
#         if value:
#             return queryset.filter(article__type_article__nom__icontains=value)
#         return queryset
#     def filter_nom(self, queryset, name, value):
#         """Filtre les mouvements par nom d'article"""
#         if value:
#             return queryset.filter(article__nom__icontains=value)
#         return queryset
#     def filter_quantite_stock_min(self, queryset, name, value):
#         """Filtre les mouvements avec une quantité de stock minimale"""
#         if value is not None:
#             return queryset.filter(article__quantite_stock__gte=value)
#         return queryset
#     def filter_quantite_stock_max(self, queryset, name, value):
#         """Filtre les mouvements avec une quantité de stock maximale"""
#         if value is not None:
#             return queryset.filter(article__quantite_stock__lte=value)
#         return queryset
#     def filter_prix_min(self, queryset, name, value):
#         """Filtre les mouvements avec un prix unitaire minimum"""
#         if value is not None:
#             return queryset.filter(article__prix_unitaire__gte=value)
#         return queryset
#     def filter_prix_max(self, queryset, name, value):
#         """Filtre les mouvements avec un prix unitaire maximum"""
#         if value is not None:
#             return queryset.filter(article__prix_unitaire__lte=value)
#         return queryset
#     def filter_niveau_alerte(self, queryset, name, value):
#         """Filtre les mouvements par niveau d'alerte"""
#         if value == 'critique':
#             return queryset.filter(article__quantite_stock__lte=F('article__seuil_critique'))
#         elif value == 'alerte':
#             return queryset.filter(
#                 article__quantite_stock__lte=F('article__seuil_alerte'),
#                 article__quantite_stock__gt=F('article__seuil_critique')
#             )
#         elif value == 'normal':
#             return queryset.filter(article__quantite_stock__gt=F('article__seuil_alerte'))
#         return queryset
#     def filter_sans_stock(self, queryset, name, value):
#         """Filtre les mouvements pour les articles sans stock"""
#         if value:
#             return queryset.filter(article__quantite_stock=0)
#         return queryset
#     def filter_stock_faible(self, queryset, name, value):
#         """Filtre les mouvements pour les articles avec un stock faible"""
#         if value:
#             return queryset.filter(article__quantite_stock__lte=F('article__seuil_critique'))
#         return queryset
#     def filter_emplacement(self, queryset, name, value):
#         """Filtre les mouvements par emplacement"""
#         if value:
#             return queryset.filter(article__emplacement__icontains=value)
#         return queryset
        