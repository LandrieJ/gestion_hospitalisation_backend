from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Patient
from .serializers import PatientSerializer


class PatientAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Récupère uniquement les patients enregistrés par l'utilisateur connecté.
        """
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Crée un patient et l'associe automatiquement à l'utilisateur connecté.
        """

        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            patient.registered_by = request.user

            if hasattr(request.user, "hospital") and request.user.hospital:
                patient.save()
                patient.hospitals.set([request.user.hospital])
                patient.hospitals_actuel.set([request.user.hospital])
            else:
                return Response(
                    {"error": "L'utilisateur n'est rattaché à aucun hôpital."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            patient.save()
            return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Met à jour un patient en fonction de son ID.
        """
        patient = Patient.objects.get(pk=pk)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Supprime un patient en fonction de son ID.
        """
        patient = Patient.objects.get(pk=pk)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PatientDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """
        Récupère les détails d'un patient en fonction de son ID.
        """
        try:
            patient = Patient.objects.get(pk=pk)
            serializer = PatientSerializer(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
