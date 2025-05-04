from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer
from videoflix_db.models import UserProfil


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
        data = {}
        data = {
            'token': token.key,
            'username': saved_user.username,
            'email': saved_user.email,
            'user_id': saved_user.pk,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = UserProfil.objects.all()
        serializer = RegistrationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = UserProfil.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = RegistrationSerializer(user)
        return Response(serializer.data)


class LoginView(ObtainAuthToken):

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.pk,
            }
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_201_CREATED)
