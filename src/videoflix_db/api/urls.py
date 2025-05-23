from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegistrationView, FileUploadView, LoginView, VideoView, WatchedVideoView, ConfirmEmailView, ResetPasswordView
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'videos', VideoView, basename='video')
router.register(r'watcheds', WatchedVideoView, basename='watched')

urlpatterns = [
    path("", include(router.urls)),
    path('upload/', FileUploadView.as_view(), name='upload-list'),
    path('upload/<int:pk>/', FileUploadView.as_view(), name='upload-detail'),
    path('registration/', RegistrationView.as_view(), name='registration-detail'),
    path('login/', LoginView.as_view(), name='login-detail'),
    path('confirm/', ConfirmEmailView.as_view(), name='confirm-detail'),
    path('reset/', ResetPasswordView.as_view(), name='reset-detail'),
]
