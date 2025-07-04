from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework import routers
from .views import (
    RegistrationView, FileUploadView, LoginView, 
    VideoView, WatchedVideoView, ConfirmEmailView, 
    ResetPasswordView, ChangePasswordView, FileEditView,
    VideoStreamView, ChangePassVerifyView, UserVolumeUpdateView,
    CookieTokenObtainPairView
)


router = routers.SimpleRouter()
router.register(r'videos', VideoView, basename='video')


urlpatterns = [
    path("", include(router.urls)),
    path('registration/', RegistrationView.as_view(), name='registration-detail'),

    


    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),




    path('login/', LoginView.as_view(), name='login-detail'),
    path('confirm/', ConfirmEmailView.as_view(), name='confirm-detail'),
    path('change/', ChangePasswordView.as_view(), name='change-detail'),
    path('verify/', ChangePassVerifyView.as_view(), name='verify-detail'),
    path('reset/', ResetPasswordView.as_view(), name='reset-detail'),
    path('upload/', FileUploadView.as_view(), name='upload-list'),
    path('upload/<int:pk>/', FileEditView.as_view(), name='upload-detail'),
    path('volume/', UserVolumeUpdateView.as_view(), name='volume-detail'),
    path('videos/<int:pk>/stream/<str:quality>/', VideoStreamView.as_view(), name='video-stream'),
    path('watched/<int:pk>/', WatchedVideoView.as_view(), name='watched-detail'),
]
