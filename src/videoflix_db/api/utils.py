from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
from base64 import urlsafe_b64encode
import hmac
import hashlib


def generate_video_url(obj, quality, request):
    user = request.user
    if user.is_staff:
        valid_minutes = 24 * 60
    else:
        valid_minutes = 10
    expires_at = int((timezone.now() + timedelta(minutes=valid_minutes)).timestamp())
    token = generate_video_token(obj.id, quality, expires_at)
    path = reverse('video-stream', args=[obj.id, quality], request=request)
    return f"{path}?token={token}&expires={expires_at}"

def generate_video_token(video_id, quality, expires_at):
    secret_key = settings.SECRET_KEY.encode()
    message = f"{video_id}:{quality}:{expires_at}".encode()
    signature = hmac.new(secret_key, message, hashlib.sha256).digest()
    token = urlsafe_b64encode(signature).decode().rstrip('=')
    return token

def verify_video_token(video_id, quality, token, expires_at):
    try:
        expires_at = int(expires_at)
    except ValueError:
        return False
    if expires_at < int(timezone.now().timestamp()):
        return False
    expected_token = generate_video_token(video_id, quality, expires_at)
    return hmac.compare_digest(expected_token, token)

def get_video_file(video, quality):
    file_map = {
        '1080p': 'file1080p',
        '720p': 'file720p',
        '360p': 'file360p',
        '240p': 'file240p',
    }
    field_name = file_map.get(quality)
    return getattr(video, field_name, None) if field_name else None


def get_range(range_header, file_size):
    try:
        byte_range = range_header.split('=')[1]
        start_str, end_str = byte_range.split('-')
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1
        if start > end or start >= file_size:
            raise ValueError
        length = end - start + 1
        return start, end, length
    except (ValueError, IndexError):
        return 0, file_size - 1, file_size


def read_range(path, start, end, block_size=8192):
    with open(path, 'rb') as file:
        file.seek(start)
        bytes_left = end - start + 1
        while bytes_left > 0:
            chunk_size = min(block_size, bytes_left)
            data = file.read(chunk_size)
            if not data:
                break
            yield data
            bytes_left -= len(data)
