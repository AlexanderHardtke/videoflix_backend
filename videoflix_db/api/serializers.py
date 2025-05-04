from rest_framework import serializers
from videoflix_db.models import UserProfil
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfil
        fields = '__all__'