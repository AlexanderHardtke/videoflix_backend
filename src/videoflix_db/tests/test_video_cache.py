import pytest
from django.core.cache import cache
from rest_framework.test import APIRequestFactory, force_authenticate
from videoflix_db.api.views import VideoView
from videoflix_db.models import Video, WatchedVideo
from.test_data import create_user, create_video, create_admin

@pytest.fixture
def user():
    return create_user()

@pytest.fixture
def admin():
    return create_admin()

@pytest.fixture
def video(admin):
    return create_video(admin)

@pytest.fixture
def watched_video(user, video):
    return WatchedVideo.objects.create(user=user, video=video, watched_until=5)

@pytest.fixture
def api_request_factory():
    return APIRequestFactory()

@pytest.fixture
def authenticated_request(api_request_factory, user, video):
    request = api_request_factory.get(f"/api/videos/{video.pk}/")
    force_authenticate(request, user=user)
    return request

@pytest.fixture
def initial_video_response(authenticated_request, video, watched_video):
    view = VideoView.as_view({"get": "retrieve"})
    cache_key = f"video_meta:{video.pk}"
    cache.delete(cache_key)
    response = view(authenticated_request, pk=video.pk)
    return {
        "response": response,
        "view": view,
        "cache_key": cache_key,
    }

@pytest.mark.django_db
def test_video_retrieve_caches(user, video, watched_video, initial_video_response):
    response= initial_video_response["response"]
    view = initial_video_response["view"]
    assert response.status_code == 200
    assert response.data["watched_until"] == 5
    Video.objects.filter(pk=video.pk).update(name="Changed")
    WatchedVideo.objects.filter(pk=watched_video.pk).update(watched_until=10)
    request = APIRequestFactory().get(f"/api/videos/{video.pk}/")
    force_authenticate(request, user=user)
    response = view(request, pk=video.pk)
    assert response.status_code == 200
    assert response.data["name"] == "exampleName"
    assert response.data["watched_until"] == 10