from rest_framework import serializers
from videoflix_db.models import UserProfil, Video
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfil
        fields = '__all__'


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
