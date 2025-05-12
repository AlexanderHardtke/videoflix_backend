from rest_framework import serializers
from videoflix_db.models import UserProfil, Video
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"repeated_password": "Passwörter stimmen nicht überein."}
            )

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"registration": "Confirm your email address"}
            )

        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        UserProfil.objects.create(user=user, type=user_type,)

        return user
        

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['name', 'type', 'image', 'file1080p']


class VideoSerializer():

    class Meta:
        model = Video
        fields = '__all__'


class WatchedVideoSerializer():

    class Meta:
        model = Video
        fields = '__all__'