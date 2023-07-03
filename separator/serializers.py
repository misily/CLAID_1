from rest_framework import serializers
from .models import SeparationResult

class SeparationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeparationResult
        fields = '__all__'