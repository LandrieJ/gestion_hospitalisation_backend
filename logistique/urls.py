from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TypeArticleViewSet,
    FournisseurViewSet,
    ArticleViewSet,
    MouvementStockViewSet
)

router = DefaultRouter()
router.register(r'types-articles', TypeArticleViewSet, basename='type-article')
router.register(r'fournisseurs', FournisseurViewSet, basename='fournisseur')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'mouvements', MouvementStockViewSet, basename='mouvement')

urlpatterns = [
    path('', include(router.urls)),
]