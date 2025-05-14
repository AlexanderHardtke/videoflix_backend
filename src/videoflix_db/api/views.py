from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer, FileUploadSerializer, VideoSerializer, WatchedVideoSerializer, VideoListSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from videoflix_db.models import Video, WatchedVideo


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
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None, format=None):
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
    permission_classes = [IsAuthenticated]

    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        return VideoSerializer

    def retrieve(self, request, *args, **kwargs):
        video = self.get_object()
        WatchedVideo.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={"watched_until": 0}
        )

        serializer = self.get_serializer(video)
        data = serializer.data
        data['watched_until'] = watched_video.watched_until 
        return Response(serializer.data)


class WatchedVideoView(viewsets.GenericViewSet,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]

    serializer_class = WatchedVideoSerializer

    def get_queryset(self):
        return WatchedVideo.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
