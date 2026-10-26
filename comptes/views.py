from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Education, Competence, Horaire
from .serializers import (
    CustomUserSerializer,
    EducationSerializer,
    CompetenceSerializer,
    HoraireSerializer,
)
from rest_framework import status
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import base64
import os


class UserView(APIView):
    """Gestion des utilisateurs : Liste et création"""

    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        is_active = request.query_params.get("is_active")
        status = request.query_params.get("status")

        
        if request.user.user_type != CustomUser.SUPER_ADMIN:
            users = CustomUser.objects.filter(hospital=request.user.hospital)
        else:
            users = CustomUser.objects.all()

        if is_active is not None:
            is_active = (
                is_active.lower() == "true"
            )
            users = users.filter(is_active=is_active)
        elif status is not None:
            users = users.filter(status=status)

        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Créer un utilisateur (uniquement pour les super admins)"""
        email = request.data.get("email")
        matricule_professionnel = request.data.get("matricule_professionnel")
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"detail": "Un utilisateur avec cet email existe déjà."}, status=400
            )

        if User.objects.filter(
            matricule_professionnel=matricule_professionnel
        ).exists():
            return JsonResponse(
                {
                    "detail": "Un utilisateur avec ce matricule professionnel existe déjà."
                },
                status=400,
            )

        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """Gestion des utilisateurs : Liste, création, modification et suppression"""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, user_id):
        """Mettre à jour un utilisateur (seul un super admin peut modifier un autre utilisateur)"""
        user = get_object_or_404(CustomUser, id=user_id)

        if request.user != user and request.user.user_type not in [
            CustomUser.SUPER_ADMIN,
            CustomUser.ADMIN,
        ]:
            raise PermissionDenied(
                "Vous n'avez pas les droits pour modifier cet utilisateur."
            )

        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        """Supprimer un utilisateur (seul un super admin peut supprimer un utilisateur)"""
        user = get_object_or_404(CustomUser, id=user_id)

        if request.user.user_type != CustomUser.SUPER_ADMIN:
            raise PermissionDenied(
                "Vous n'avez pas les droits pour supprimer cet utilisateur."
            )

        user.delete()
        return Response(
            {"message": "Utilisateur supprimé avec succès."},
            status=status.HTTP_204_NO_CONTENT,
        )


class EducationView(APIView):
    """Gestion des éducations d’un utilisateur"""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        educations = Education.objects.filter(user_id=user_id)
        serializer = EducationSerializer(educations, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        mutable_data = request.data.copy()
        mutable_data["user"] = user_id

        serializer = EducationSerializer(data=mutable_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EducationDetailView(APIView):
    """Détail, modification et suppression d’une éducation"""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, education_id):
        education = get_object_or_404(Education, id=education_id, user_id=user_id)
        serializer = EducationSerializer(education)
        return Response(serializer.data)

    def patch(self, request, user_id, education_id):
        education = get_object_or_404(Education, id=education_id, user_id=user_id)
        serializer = EducationSerializer(education, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, education_id):
        education = get_object_or_404(Education, id=education_id, user_id=user_id)
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompetenceView(APIView):
    """Gestion des spécialités d’un utilisateur"""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        competence = Competence.objects.filter(user_id=user_id)
        serializer = CompetenceSerializer(competence, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        mutable_data = request.data.copy()
        mutable_data["user"] = user_id

        serializer = CompetenceSerializer(
            data=mutable_data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompetenceDetailView(APIView):
    """Détail, modification et suppression d’une spécialité"""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, competence_id):
        competence = get_object_or_404(Competence, id=competence_id, user_id=user_id)
        serializer = CompetenceSerializer(competence)
        return Response(serializer.data)

    def patch(self, request, user_id, competence_id):
        competence = get_object_or_404(Competence, id=competence_id, user_id=user_id)
        serializer = CompetenceSerializer(competence, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, competence_id):
        competence = get_object_or_404(Competence, id=competence_id, user_id=user_id)
        competence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HorairesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            horaire = Horaire.objects.get(user_id=user_id)
            serializer = HoraireSerializer(horaire)
            return Response(serializer.data)
        except Horaire.DoesNotExist:
            return Response(
                {"error": "Aucun horaire trouvé"}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, user_id):
        try:
            horaire = Horaire.objects.get(user_id=user_id)
            serializer = HoraireSerializer(horaire, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Horaire.DoesNotExist:
            return Response(
                {"error": "Aucun horaire trouvé"}, status=status.HTTP_404_NOT_FOUND
            )


def generate_secure_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def encode_image_to_base64(image_path):
    """
    Convertit une image en chaîne Base64
    """
    try:
        full_path = os.path.join(settings.BASE_DIR, "templates", image_path)

        with open(full_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        file_extension = os.path.splitext(image_path)[1][1:].lower()
        mime_type = f"image/{file_extension}"

        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Erreur lors du chargement de l'image : {e}")
        return None


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        User = get_user_model()
        email = request.data.get("email")

        if not email:
            return Response(
                {"detail": "L'email est requis."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Aucun utilisateur avec cet email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_password = generate_secure_password()
        user.set_password(new_password)
        user.save()
        logo_base64 = encode_image_to_base64("logo/logoMinistere.png")

        html_content = render_to_string(
            "emails/password_reset_email.html",
            {
                "nouveau_mot_de_passe": new_password,
                "nom_utilisateur": user.username or user.email,
                "url_connexion": "http://localhost:1003/login",
                "logo": logo_base64,
                "hospital": user.hospital.name if user.hospital else None,
            },
        )


        text_content = strip_tags(html_content)

        try:
            email_message = EmailMultiAlternatives(
                subject="Réinitialisation de votre mot de passe",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_message.attach_alternative(html_content, "text/html")

            email_message.send(fail_silently=False)

        except Exception as e:
            return Response(
                {"detail": "Erreur lors de l'envoi de l'email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Mot de passe réinitialisé avec succès. Vérifiez votre email."},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        User = get_user_model()

        if not email or not password:
            return JsonResponse({"detail": "Email et mot de passe requis."}, status=400)

        try:
            user = User.objects.get(email=email)

            if not user.is_active:
                messages = {
                    "blocked": "Votre compte a été bloqué par l'admin.",
                    "rejected": "Votre demande d'inscription a été rejetée par l'admin.",
                    "new": "Votre compte est en attente de validation par l'admin.",
                }
                return JsonResponse(
                    {"detail": messages.get(user.status, "Votre compte est inactif.")},
                    status=403,
                )

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Connexion réussie"}, status=200)

            return JsonResponse(
                {"detail": "Email ou mot de passe incorrect."}, status=400
            )

        except User.DoesNotExist:
            return JsonResponse({"detail": "Ce compte n'existe pas."}, status=400)

    def get(self, request):
        return JsonResponse(
            {"detail": "La méthode GET n'est pas autorisée pour cette route."},
            status=405,
        )


class LogoutView(APIView):
    """Déconnexion utilisateur"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {
                "message": "Déconnexion réussie",
            }
        )


def get_csrf_token(request):
    response = JsonResponse({"csrfToken": get_token(request)})
    response["X-CSRFToken"] = get_token(request)
    return response


class SessionView(APIView):
    """Récupérer les infos de l'utilisateur connecté"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
