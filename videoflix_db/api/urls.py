from django.urls import path, include
from rest_framework import routers
from .views import (
    RegistrationView, FileUploadView, LoginView, 
    VideoView, WatchedVideoView, ConfirmEmailView, 
    ResetPasswordView, ChangePasswordView, FileEditView,
    VideoStreamView, ChangePassVerifyView, UserVolumeUpdateView,
    CookieTokenRefreshView, LogoutView
)


router = routers.SimpleRouter()
router.register(r'videos', VideoView, basename='video')


urlpatterns = [
    path("", include(router.urls)),
    path('registration/', RegistrationView.as_view(), name='registration-detail'),
    path('confirm/', ConfirmEmailView.as_view(), name='confirm-detail'),
    path('reset/', ResetPasswordView.as_view(), name='reset-detail'),
    path('verify/', ChangePassVerifyView.as_view(), name='verify-detail'),
    path('change/', ChangePasswordView.as_view(), name='change-detail'),
    
    path('login/', LoginView.as_view(), name='login-detail'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout-detail'),
    
    path('upload/', FileUploadView.as_view(), name='upload-list'),
    path('upload/<int:pk>/', FileEditView.as_view(), name='upload-detail'),
    path('volume/', UserVolumeUpdateView.as_view(), name='volume-detail'),
    path('videos/<int:pk>/stream/<str:quality>/', VideoStreamView.as_view(), name='video-stream'),
    path('watched/<int:pk>/', WatchedVideoView.as_view(), name='watched-detail'),
]
