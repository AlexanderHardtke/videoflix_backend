from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from videoflix_db.models import Video, WatchedVideo
from .serializers import RegistrationSerializer, FileUploadSerializer, VideoSerializer, WatchedVideoSerializer, VideoListSerializer, FileEditSerializer
from .pagination import TypeBasedPagination
from .utils  import get_video_file, get_range, read_range, verify_video_token, get_ip_adress
from wsgiref.util import FileWrapper
import os
from django.contrib.auth import get_user_model
from authemail import wrapper
from authemail.views import Signup, SignupVerify, Login, PasswordReset, PasswordResetVerify


CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)
User = get_user_model()


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': _("Passwords don't match")}, status=status.HTTP_400_BAD_REQUEST,
            )
        lang = request.data.get('lang', 'de')
        data = serializer.validated_data.copy()
        data.setdefault('username', data.get('email'))
        data.setdefault('first_name', '')
        data.setdefault('last_name', '')
        try:
            response = wrapper.Authemail().signup(**data)
            return Response({'success': _('Confirm your email address')}, status=status.HTTP_201_CREATED)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    def post(self, request):
        lang = request.data.get('lang', 'de')
        token = request.data.get('token')
        if not token:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)
        try:
            wrapper.Authemail().signup_verify(code=token)
            return Response({'success': _('Email confirmed')}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        lang = request.data.get('lang', 'de')
        email = request.data.get('email')
        if not email:
            return Response({'error': _('Email is missing')}, status=status.HTTP_400_BAD_REQUEST)
        try:
            wrapper.Authemail().password_reset(email=email)
            return Response({'success': _('Check your email to reset password')}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': _('Check your email to reset password')}, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    def post(self, request):
        password = request.data.get('password')
        token = request.data.get('token')
        if not token:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({'error': _('Password is missing')}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'success': _('Password changed successfully')}, status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'error': _('Incorrect username or password')}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        if not user.is_verified:
            return Response({'error': _('Confirm your email address')},status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'email': user.email,
            'user_id': user.pk,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class FileUploadView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        file = self.request.FILES.get('file1080p')
        if file and not file.content_type.startswith('video/'):
            raise UnsupportedMediaType(media_type=file.content_type)
        serializer.save()
    

class FileEditView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = FileEditSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        file = self.request.FILES.get('file1080p')
        if file and not file.content_type.startswith('video/'):
            raise UnsupportedMediaType(media_type=file.content_type)
        serializer.save()

    def delete(self, request, pk=None, format=None):
        file_instance = get_object_or_404(Video, pk=pk)
        file_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Video.objects.all().order_by('video_type', 'uploaded_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        return VideoSerializer
    
    def list(self, request, *args, **kwargs):
        paginator = TypeBasedPagination()
        paginated_queryset = paginator.paginate_queryset(self.queryset, request, view=self)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

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
        meta_with_progress['watched_until_id'] = watched_video.id
        return Response(meta_with_progress)


class VideoStreamView(APIView):

    def get(self, request, pk, quality):
        token = request.query_params.get('token')
        expires = request.query_params.get('expires')
        ip_address = get_ip_adress(request)

        if not token or not expires:
            return Response({'error': _('Missing or invalid token.')}, status=status.HTTP_401_UNAUTHORIZED)

        if not verify_video_token(pk, quality, token, expires, ip_address):
            return Response({'error': _('Missing or invalid token.')}, status=status.HTTP_401_UNAUTHORIZED)

        video = get_object_or_404(Video, pk=pk)
        file_field = get_video_file(video, quality)
        if not file_field:
            return Response({'error': _('Quality is not available')}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = file_field.path
        file_size = os.path.getsize(file_path)

        range_header = request.headers.get('Range')
        if range_header and 'bytes=' in range_header:
            start, end, length = get_range(range_header, file_size)
            response = StreamingHttpResponse(
                read_range(file_path, start, end), status=206, content_type='video/mp4')
            response['Content-Length'] = str(length)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            return response
        
        response = StreamingHttpResponse(
            FileWrapper(open(file_path, 'rb')), content_type='video/mp4')
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response
                

class WatchedVideoView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = WatchedVideoSerializer

    def get_queryset(self):
        return WatchedVideo.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
