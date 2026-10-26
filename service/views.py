from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from .models import Service, Bed
from .serializers import ServiceSerializers, BedSerializer
from comptes.models import CustomUser


class ServiceViewSet(viewsets.ModelViewSet):
    """
    Gestion des Services :
    - SUPER_ADMIN : peut tout faire (CRUD complet)
    - ADMIN : peut voir et modifier les services de son hôpital
    - SIMPLE_USER : peut uniquement consulter
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializers
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user

        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return Service.objects.all()

        if user.user_type == CustomUser.SUPER_ADMIN:
            return Service.objects.all()
        
        if user.user_type == CustomUser.ADMIN:
            if hasattr(user, "hospital") and user.hospital:
                return Service.objects.filter(hospital=user.hospital.id)

        if user.user_type == CustomUser.SIMPLE_USER:
            if hasattr(user, "service") and user.service:
                return Service.objects.filter(pk=user.service.id)

        return Service.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.user_type == CustomUser.SIMPLE_USER:
            raise PermissionDenied("Seul un super admin peut créer un service.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.user_type not in [CustomUser.SUPER_ADMIN, CustomUser.ADMIN]:
            raise PermissionDenied("Vous n'avez pas les droits pour modifier ce service.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.user_type == CustomUser.SIMPLE_USER:
            raise PermissionDenied("Seul un super admin peut supprimer un service.")
        return super().destroy(request, *args, **kwargs)


class BedViewSet(viewsets.ModelViewSet):
    """
    Gestion des Lits (Bed) :
    Accès complet par défaut pour tous les utilisateurs authentifiés
    """

    queryset = Bed.objects.all()
    serializer_class = BedSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Bed.objects.none()
        return Bed.objects.all()
    
    
# class BedViewSet(viewsets.ModelViewSet):
#     """
#     Gestion des Lits (Bed) :
#     - SUPER_ADMIN : CRUD complet sur tous les lits
#     - ADMIN : CRUD limité aux lits de son hôpital
#     - SIMPLE_USER : lecture seule limitée aux lits de son service
#     """

#     queryset = Bed.objects.all()
#     serializer_class = BedSerializer

#     def get_queryset(self):
#         user = self.request.user

#         if not user.is_authenticated:
#             return Bed.objects.none()

#         if user.user_type == CustomUser.SUPER_ADMIN:
#             # Super admin → voit tous les lits
#             return Bed.objects.all()

#         if user.user_type == CustomUser.ADMIN:
#             # Admin → lits des services de son hôpital
#             if hasattr(user, "hospital") and user.hospital:
#                 return Bed.objects.filter(service__hospital=user.hospital)

#         if user.user_type == CustomUser.SIMPLE_USER:
#             # Simple user → uniquement les lits de son service
#             if hasattr(user, "service") and user.service:
#                 return Bed.objects.filter(service=user.service)

#         return Bed.objects.none()

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         if user.user_type == CustomUser.SUPER_ADMIN:
#             return super().create(request, *args, **kwargs)

#         if user.user_type == CustomUser.ADMIN:
#             service_id = request.data.get("service")
#             if not service_id:
#                 raise PermissionDenied("Vous devez spécifier un service.")

#             # Vérifie que le service appartient bien à l’hôpital de l’admin
#             if not user.hospital.service.filter(id=service_id).exists():
#                 raise PermissionDenied("Vous ne pouvez créer un lit que dans votre hôpital.")

#             return super().create(request, *args, **kwargs)

#         raise PermissionDenied("Vous n'avez pas les droits pour créer un lit.")

#     # def update(self, request, *args, **kwargs):
#     #     bed = self.get_object()
#     #     user = request.user

#     #     if user.user_type == CustomUser.SUPER_ADMIN:
#     #         return super().update(request, *args, **kwargs)

#     #     if user.user_type == CustomUser.ADMIN:
#     #         # Vérifie que le lit appartient à son hôpital
#     #         if bed.service.hospital != user.hospital:
#     #             raise PermissionDenied("Vous ne pouvez modifier que les lits de votre hôpital.")
#     #         return super().update(request, *args, **kwargs)

#     #     raise PermissionDenied("Vous n'avez pas les droits pour modifier ce lit.")

#     def partial_update(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def destroy(self, request, *args, **kwargs):
#         bed = self.get_object()
#         user = request.user

#         if user.user_type == CustomUser.SUPER_ADMIN:
#             return super().destroy(request, *args, **kwargs)

#         if user.user_type == CustomUser.ADMIN:
#             # Vérifie que le lit appartient à son hôpital
#             if bed.service.hospital != user.hospital:
#                 raise PermissionDenied("Vous ne pouvez supprimer que les lits de votre hôpital.")
#             return super().destroy(request, *args, **kwargs)

#         raise PermissionDenied("Vous n'avez pas les droits pour supprimer ce lit.")