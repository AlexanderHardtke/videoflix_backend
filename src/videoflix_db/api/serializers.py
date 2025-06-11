from rest_framework import serializers
from videoflix_db.models import UserProfil, Video, WatchedVideo


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
                {'repeated_password': "Passwords don't match"}
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
    url = serializers.HyperlinkedIdentityField(view_name='upload-detail')
    bigImage = serializers.FileField(required=False, allow_null=True, help_text="Optional: Big image for the video")
    file1080p = serializers.FileField(required=True, help_text="Required: Highest Quality Video for compression")

    class Meta:
        model = Video
        fields = ['id', 'url', 'name', 'type', 'descriptionEN', 'descriptionDE', 'bigImage', 'file1080p']


class FileEditSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Video
        fields = ['id', 'name', 'type', 'descriptionEN', 'descriptionDE']


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        exclude = [
            'descriptionEN', 'descriptionDE', 'type',
            'bigImage', 'image', 'filePreview144p', 'uploaded_at'
        ]


class VideoListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='video-detail')

    class Meta:
        model = Video
        fields = [
            'name', 'url', 'type', 'image', 'bigImage', 
            'filePreview144p', 'descriptionEN',
            'descriptionDE', 'uploaded_at'
        ]


class WatchedVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = WatchedVideo
        fields = ['id', 'video', 'watched_until']
        read_only_fields = ['id', 'video', 'user']
