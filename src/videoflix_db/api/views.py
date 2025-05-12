from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer, FileUploadSerializer, VideoSerializer, WatchedVideoSerializer
from rest_framework.permissions import IsAdminUser
from videoflix_db.models import UserProfil, Video, WatchedVideo


class RegistrationView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved_user = serializer.save()
        token, created = Token.objects.get_or_create(user=saved_user)
        return Response({"registration": "Confirm your email address"}, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
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
        serializer = FileUploadSerializer(data=request.date)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoView(viewsets.ReadOnlyModelViewSet):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class WatchedVideoView(viewsets.ModelViewSet):

    queryset = WatchedVideo.objects.all()
    serializer_class = WatchedVideoSerializer
