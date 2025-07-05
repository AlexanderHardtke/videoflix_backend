from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from videoflix_db.models import Video, WatchedVideo
from .utils import generate_video_url


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'username' in self.fields:
            self.fields.pop('username')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'error': _('Incorrect email or password')})

        if not user.check_password(password):
            raise serializers.ValidationError(
                {'error': _('Incorrect email or password')})

        if not user.is_active:
            raise serializers.ValidationError(
                {'error': _('Confirm your email address')})

        attrs['username'] = user.username
        data = super().validate(attrs)
        return data


class FileUploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='upload-detail')
    big_image = serializers.FileField(
        required=False, allow_null=True, help_text="Optional: Big image for the video")
    file1080p = serializers.FileField(
        required=True, help_text="Required: Highest Quality Video for compression")

    class Meta:
        model = Video
        fields = ['id', 'url', 'name', 'video_type', 'description_en',
                  'description_de', 'big_image', 'file1080p']


class FileEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = ['id', 'name', 'video_type',
                  'description_en', 'description_de']


class VideoSerializer(serializers.ModelSerializer):
    video_urls = serializers.SerializerMethodField()
    sound_volume = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'name', 'video_urls', 'sound_volume']

    def get_video_urls(self, obj):
        request = self.context.get('request')
        return {
            '1080p': generate_video_url(obj, '1080p', request) if obj.file1080p else None,
            '720p': generate_video_url(obj, '720p', request) if obj.file720p else None,
            '360p': generate_video_url(obj, '360p', request) if obj.file360p else None,
            '240p': generate_video_url(obj, '240p', request) if obj.file240p else None,
        }

    def get_sound_volume(self, obj):
        return self.context['request'].user.sound_volume


class VideoListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    watched_until = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'name', 'url', 'video_type', 'image', 'big_image',
            'file_preview144p', 'watched_until', 'description_en',
            'description_de', 'uploaded_at', 'duration'
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        path = reverse('video-detail', kwargs={'pk': obj.pk})
        scheme = 'https' if request.is_secure() or request.META.get(
            'HTTP_X_FORWARDED_PROTO') == 'https' else 'http'
        host = request.get_host()
        return f"{scheme}://{host}{path}"

    def get_watched_until(self, video):
        user = self.context['request'].user
        watched = WatchedVideo.objects.filter(user=user, video=video).first()
        return watched.watched_until if watched else None


class WatchedVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = WatchedVideo
        fields = ['id', 'video', 'watched_until']
        read_only_fields = ['id', 'video', 'user']
