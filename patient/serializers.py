from rest_framework import serializers
from .models import Patient



class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ['registered_by', 'hospitals', 'date_registered']
