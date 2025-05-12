from rest_framework import serializers
from videoflix_db.models import UserProfil, Video


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfil
        fields = ['email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"repeated_password": "Passwörter stimmen nicht überein."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        email = validated_data['email']

        userprofil = UserProfil.objects.filter(email=email).first()
        if userprofil:
            return userprofil

        user = UserProfil.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
        )
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
