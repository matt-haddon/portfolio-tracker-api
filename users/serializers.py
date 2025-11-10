from rest_framework import serializers

from .models import CustomUser


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name"]
        read_only_fields = ["id", "email"]
