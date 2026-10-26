# # back-end/logistique/permissions.py
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# from rest_framework.permissions import BasePermission

# from rest_framework import permissions

# class LogisticsPermission(permissions.BasePermission):
#     """
#     Permission pour les opérations de logistique.
#     """

#     def has_permission(self, request, view):
#         # Autoriser uniquement les utilisateurs authentifiés
#         return request.user and request.user.is_authenticated

#     def has_object_permission(self, request, view, obj):
#         # Autoriser uniquement les utilisateurs ayant accès à l'hôpital de l'objet
#         return obj.hospital == request.user.hospital
    
# class IsLogisticsStaff(BasePermission):
#     """
#     Permission pour vérifier si l'utilisateur est membre du personnel de logistique.
#     """

#     def has_permission(self, request, view):
#         # Vérifie si l'utilisateur est authentifié et a le rôle de personnel de logistique
#         return request.user and request.user.is_authenticated and request.user.is_logistics_staff

#     def has_object_permission(self, request, view, obj):
#         # Vérifie si l'utilisateur a accès à l'objet en fonction de son hôpital
#         return obj.hospital == request.user.hospital