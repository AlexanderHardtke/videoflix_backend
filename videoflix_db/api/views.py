import os
from wsgiref.util import FileWrapper
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from django.http import HttpRequest, StreamingHttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authemail.views import SignupVerify, PasswordReset, PasswordResetVerify, PasswordResetVerified
from authemail.views import Signup as AuthemailSignup
from authemail.serializers import PasswordResetSerializer
from videoflix_db.auth import CookieJWTAuthentication
from videoflix_db.models import Video, WatchedVideo
from .serializers import (
    FileUploadSerializer, VideoSerializer, WatchedVideoSerializer,
    VideoListSerializer, FileEditSerializer, CustomTokenObtainPairSerializer
)
from .pagination import TypeBasedPagination
from .utils import get_video_file, get_range, read_range, verify_video_token, get_ip_adress


User = get_user_model()


class RegistrationView(APIView):
    def post(self, request):
        data = request.data.copy()
        email = request.data.get('email')
        password = request.data.get('password')
        repeated_password = data.get('repeated_password')

        if not email or not password:
            return Response({'error': _("Email and password required")}, status=status.HTTP_400_BAD_REQUEST)
        if password != repeated_password:
            return Response({'error': _("Passwords don't match")}, status=status.HTTP_400_BAD_REQUEST)
        
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        data['username'] = username

        view = AuthemailSignup()
        return view.post(request)
        

class ConfirmEmailView(APIView):
    def get(self, request: HttpRequest):
        code = request.GET.get('code')
        if not code:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)

        signup_verify_view = SignupVerify.as_view()
        response = signup_verify_view(request._request)
        
        if response.status_code == status.HTTP_200_OK:
            return Response({'success': _('Email confirmed')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)
        

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': _('Check your email to reset password')}, status=status.HTTP_201_CREATED)
        
        view = PasswordReset()
        response = view.post(request)
        if response.status_code == status.HTTP_201_CREATED:
            return Response({'success': _('Check your email to reset password')}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': response.data}, status=status.HTTP_400_BAD_REQUEST)


class ChangePassVerifyView(APIView):
    def get(self, request: HttpRequest):
        code = request.GET.get('code')
        if not code:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)
        
        change_pass_view = PasswordResetVerify.as_view()
        response = change_pass_view(request._request)
        if response.status_code == status.HTTP_200_OK:
            return Response({'success': _('User verified')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)
        

class ChangePasswordView(APIView):
    def post(self, request):
        if not request.data.get('code'):
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('password') or not request.data.get('repeatPw'):
            return Response({'error': _('Password is missing')}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('password') != request.data.get('repeatPw'):
                return Response({'error': _("Passwords don't match")}, status=status.HTTP_400_BAD_REQUEST)
                                
        view = PasswordResetVerified()
        response = view.post(request)
        if response.status_code == status.HTTP_200_OK:
            return Response({'success': _('Password changed successfully')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': _('Token is not valid or expired')}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']
        user = serializer.user
        
        if not user.is_active:
            return Response({'error': _('Confirm your email address')}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({'success': _('Login successful')})

        development = getattr(settings, 'DEBUG', True)
        secure = not development
        samesite = 'Lax' if development else 'None'
        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=secure,
            samesite=samesite
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=secure,
            samesite=samesite
        )

        return response
    

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        development = getattr(settings, 'DEBUG', True)
        secure = not development
        samesite = 'Lax' if development else 'None'
        response = Response({'success': _('Logged out')}, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=str(''),
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=0
        )

        response.set_cookie(
            key='refresh_token',
            value=str(''),
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=0
        )
        
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token or refresh_token is None:
            return Response({'error': _('Refresh token not found!')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({'error': _('Refresh token invalid!')}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data.get('access')
        response = Response({'success': _('access Token refreshed')})
        development = getattr(settings, 'DEBUG', True)
        secure = not development
        samesite = 'Lax' if development else 'None'
        response.set_cookie(
            key='access_token',
            value=str(access_token),
            httponly=True,
            secure=secure,
            samesite=samesite
        )
        return response


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
    authentication_classes = [CookieJWTAuthentication]
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
        CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)
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
        meta_with_progress['sound_volume'] = request.user.sound_volume 
        return Response(meta_with_progress)


class VideoStreamView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    

class UserVolumeUpdateView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        sound_volume = request.data.get('sound_volume')
        if sound_volume is not None:
            request.user.sound_volume = sound_volume
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': _('No volume provided')}, status=status.HTTP_400_BAD_REQUEST)
                

class WatchedVideoView(generics.UpdateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = WatchedVideoSerializer

    def get_queryset(self):
        return WatchedVideo.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
