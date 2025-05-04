from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegistrationView, UserViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path("", include(router.urls)),
    path('registration/', RegistrationView.as_view(), name='registration-detail')
]