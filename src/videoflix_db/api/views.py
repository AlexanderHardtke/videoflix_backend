from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from videoflix_db.models import Video, WatchedVideo, PasswordForgetToken, EmailConfirmationToken, UserProfil
from .serializers import RegistrationSerializer, FileUploadSerializer, VideoSerializer, WatchedVideoSerializer, VideoListSerializer
from .permissions import IsEmailConfirmed
import secrets
import requests


CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)


class RegistrationView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved_user = serializer.save()
        token = secrets.token_hex(32)
        EmailConfirmationToken.objects.create(user=saved_user, token=token)
        lang = request.data.get('lang', 'de')
        url = 'https://videoflix.alexander-hardtke.com/confirm-email-link-de.php' if lang == 'de' else \
              'https://videoflix.alexander-hardtke.com/confirm-email-link-en.php'

        try:
            requests.post(
                url,
                json={
                    'email': saved_user.email,
                    'token': token,
                },
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
        except requests.RequestException as error:
            return Response({'registration': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'registration': 'Confirm your email address'}, status=status.HTTP_201_CREATED)


class ConfirmEmailView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is not valid or expired'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            confirmation_token = EmailConfirmationToken.objects.get(
                token=token)
        except EmailConfirmationToken.DoesNotExist:
            return Response({'error': 'Token is not valid or expired'}, status=status.HTTP_400_BAD_REQUEST)

        if confirmation_token.is_expired():
            confirmation_token.delete()
            return Response({'error': 'Token is not valid or expired'}, status=status.HTTP_400_BAD_REQUEST)

        user = confirmation_token.user
        user.email_confirmed = True
        user.save()
        confirmation_token.delete()

        return Response({'success': 'email address confirmed'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        lang = request.data.get('lang', 'de')
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            saved_user = UserProfil.objects.get(email=email)
        except UserProfil.DoesNotExist:
            return Response({'reset': 'Check your email to reset password'}, status=status.HTTP_201_CREATED)

        token = secrets.token_hex(32)
        PasswordForgetToken.objects.create(user=saved_user, token=token)
        url = 'https://videoflix.alexander-hardtke.com/send-reset-link-de.php' if lang == 'de' else \
              'https://videoflix.alexander-hardtke.com/send-reset-link-en.php'

        try:
            requests.post(
                url,
                json={
                    'email': saved_user.email,
                    'token': token,
                },
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
        except requests.RequestException as error:
            return Response({'reset': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'reset': 'Check your email to reset password'}, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    def post(self, request):
        password = request.data.get('password')
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is not valid or expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({'error': 'Password is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            confirmation_token = PasswordForgetToken.objects.get(
                token=token)
        except PasswordForgetToken.DoesNotExist:
            return Response({'error': 'Token is not valid or expired'}, status=status.HTTP_400_BAD_REQUEST)

        if confirmation_token.is_expired():
            confirmation_token.delete()
            return Response({'error': 'Token is not valid or expired'}, status=status.HTTP_400_BAD_REQUEST)

        user = confirmation_token.user
        user.set_password(password)
        user.save()
        confirmation_token.delete()

        return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response({'error': 'Incorrect username or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        if not user.email_confirmed:
            return Response(
                {'registration': 'Confirm your email address'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'username': user.username,
            'user_id': user.pk,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class FileUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        file = request.FILES.get('file1080p')
        if file and not file.content_type.startswith('video/'):
            raise UnsupportedMediaType(media_type=file.content_type)
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        file_instance = get_object_or_404(Video, pk=pk)
        serializer = FileUploadSerializer(
            file_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format=None):
        file_instance = get_object_or_404(Video, pk=pk)
        file_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsEmailConfirmed]

    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        return VideoSerializer

    def retrieve(self, request, *args, **kwargs):
        video_id = kwargs['pk']
        cache_key = f'video_meta:{video_id}'

        meta = cache.get(cache_key)
        if meta is None:
            video = self.get_object()
            meta = self.get_serializer(video).data
            cache.set(cache_key, meta, timeout=CACHETTL)

        watched_video, _ = WatchedVideo.objects.get_or_create(
            user=request.user,
            video_id=video_id,
            defaults={'watched_until': 0}
        )

        meta_with_progress = meta.copy()
        meta_with_progress['watched_until'] = watched_video.watched_until
        return Response(meta_with_progress)


class WatchedVideoView(viewsets.GenericViewSet,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin):
    permission_classes = [IsAuthenticated, IsEmailConfirmed]

    serializer_class = WatchedVideoSerializer

    def get_queryset(self):
        return WatchedVideo.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
