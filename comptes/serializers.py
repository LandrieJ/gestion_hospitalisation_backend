from rest_framework import serializers
from .models import (
    CustomUser,
    Education,
    Certification,
    Specialite,
    Horaire,
    Competence,
    Statistique,
    Blocage,
)
from hospital.models import Hospital
from service.models import Service


from hospital.serializers import HospitalSerializer
from patient.serializers import PatientSerializer
from service.serializers import ServiceSerializers


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"


class SpecialiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialite
        fields = "__all__"


class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ["debut", "fin", "jours"]

    def update(self, instance, validated_data):
        instance.debut = validated_data.get("debut", instance.debut)
        instance.fin = validated_data.get("fin", instance.fin)
        instance.jours = validated_data.get("jours", instance.jours)
        instance.save()
        return instance


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = "__all__"


class StatistiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistique
        fields = "__all__"


class BlocageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blocage
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    specialites = SpecialiteSerializer(many=True, read_only=True)
    horaires = HoraireSerializer(read_only=True)
    competences = CompetenceSerializer(many=True, read_only=True)
    statistiques = StatistiqueSerializer(read_only=True)
    blocage = BlocageSerializer(many=True, read_only=True)
    service = ServiceSerializers(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source="service",
        write_only=True,
        allow_null=True,
    )
    hospital = HospitalSerializer(read_only=True)
    hospital_id = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(),
        source="hospital",
        write_only=True,
        allow_null=True,
    )
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    patients_registered = PatientSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [ 
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "fonction",
            "matricule_professionnel",
            "biographie",
            "education",
            "certifications",
            "specialites",
            "horaires",
            "competences",
            "statistiques",
            "password",
            "blocage",
            "profile_picture",
            "user_type",
            "hospital",
            "service",
            "patients_registered",
            "date_joined",
            "hospital_id",
            "service_id",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "status",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def get_patient_registered(self, obj):
        patients = obj.patient_registered.all()
        return PatientSerializer(patients, many=True).data

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        profile_picture = validated_data.pop("profile_picture", None)

        user = CustomUser(**validated_data)

        if password:
            user.set_password(password)
        else:
            raise serializers.ValidationError({"password": "Le mot de passe est requis."})

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        return user

    def update(self, instance, validated_data):
        """Mise à jour des champs d'un utilisateur en s'assurant de ne pas écraser le mot de passe."""
        profile_picture = validated_data.pop("profile_picture", None)
        password = validated_data.pop(
            "password", None
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if profile_picture:
            instance.profile_picture = profile_picture

        if password:
            instance.set_password(
                password
            )

        instance.save()
        return instance
