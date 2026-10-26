from .models import Bed, Service
from rest_framework import serializers

class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = "__all__"
        
class ServiceSerializers(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    class Meta:
        model = Service
        fields = "__all__"
