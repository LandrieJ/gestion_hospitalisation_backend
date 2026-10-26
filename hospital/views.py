from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from .models import Hospital
from .serializers import HospitalSerializer
from comptes.models import CustomUser


class HospitalViewSet(viewsets.ModelViewSet):
    """
    Gestion des hôpitaux :
    - SUPER_ADMIN : peut tout faire (lister, créer, modifier, supprimer).
    - ADMIN : peut consulter et modifier seulement son hôpital.
    - SIMPLE_USER : peut consulter uniquement son hôpital.
    - Utilisateur anonyme : peut voir la liste des hôpitaux.
    """

    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user

        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return Hospital.objects.all()

        if user.user_type == CustomUser.SUPER_ADMIN:
            return Hospital.objects.all()

        # ADMIN ou SIMPLE_USER → accès seulement à leur hôpital
        if hasattr(user, "hospital") and user.hospital:
            return Hospital.objects.filter(id=user.hospital.id)

        return Hospital.objects.none()

    def create(self, request, *args, **kwargs):
        """Créer un hôpital (uniquement pour les super admins)"""
        if request.user.user_type != CustomUser.SUPER_ADMIN:
            return Response(
                {"error": "Création d'Hôpital non autorisée."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Mettre à jour un hôpital (super admin et admin)"""
        instance = self.get_object()
        if request.user.user_type not in [CustomUser.SUPER_ADMIN, CustomUser.ADMIN]:
            raise PermissionDenied("Vous n'avez pas les droits pour modifier cet hôpital.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Mise à jour partielle (mêmes règles que update)"""
        instance = self.get_object()
        if request.user.user_type not in [CustomUser.SUPER_ADMIN, CustomUser.ADMIN]:
            raise PermissionDenied("Vous n'avez pas les droits pour modifier cet hôpital.")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un hôpital (seul un super admin peut le faire)"""
        if request.user.user_type != CustomUser.SUPER_ADMIN:
            raise PermissionDenied("Vous n'avez pas les droits pour supprimer cet hôpital.")
        return super().destroy(request, *args, **kwargs)
