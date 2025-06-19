from rest_framework import serializers
from videoflix_db.models import UserProfil, Video, WatchedVideo
from .utils import generate_video_url


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
            raise serializers.ValidationError
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
    big_image = serializers.FileField(required=False, allow_null=True, help_text="Optional: Big image for the video")
    file1080p = serializers.FileField(required=True, help_text="Required: Highest Quality Video for compression")

    class Meta:
        model = Video
        fields = ['id', 'url', 'name', 'video_type', 'description_en', 'description_de', 'big_image', 'file1080p']


class FileEditSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Video
        fields = ['id', 'name', 'video_type', 'description_en', 'description_de']


class VideoSerializer(serializers.ModelSerializer):
    video_urls = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['name', 'video_urls']

    def get_video_urls(self, obj):
        request = self.context.get('request')
        return {
            '1080p': generate_video_url(obj, '1080p', request) if obj.file1080p else None,
            '720p': generate_video_url(obj, '720p', request) if obj.file720p else None,
            '360p': generate_video_url(obj, '360p', request) if obj.file360p else None,
            '240p': generate_video_url(obj, '240p', request) if obj.file240p else None,
        }


class VideoListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='video-detail')

    class Meta:
        model = Video
        fields = [
            'name', 'url', 'video_type', 'image', 'big_image', 
            'file_preview144p', 'description_en',
            'description_de', 'uploaded_at'
        ]


class WatchedVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = WatchedVideo
        fields = ['id', 'video', 'watched_until']
        read_only_fields = ['id', 'video', 'user']
