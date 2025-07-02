from django.utils import timezone
from django.conf import settings
from rest_framework.reverse import reverse
from datetime import timedelta
from base64 import urlsafe_b64encode
import hmac
import hashlib


def generate_video_url(obj, quality, request, valid_minutes=90):
    expires_at = int((timezone.now() + timedelta(minutes=valid_minutes)).timestamp())
    ip_address = get_ip_adress(request)
    token = generate_video_token(obj.id, quality, expires_at, ip_address)
    path = reverse('video-stream', kwargs={'pk': obj.id, 'quality': quality})
    scheme = 'https' if request.is_secure() or request.META.get('HTTP_X_FORWARDED_PROTO') == 'https' else 'http'
    host = request.get_host()
    full_url = f"{scheme}://{host}{path}?token={token}&expires={expires_at}"
    return full_url

def generate_video_token(video_id, quality, expires_at, ip_address):
    secret_key = settings.SECRET_KEY.encode()
    message = f"{video_id}:{quality}:{expires_at}:{ip_address}".encode()
    signature = hmac.new(secret_key, message, hashlib.sha256).digest()
    token = urlsafe_b64encode(signature).decode().rstrip('=')
    return token

def verify_video_token(video_id, quality, token, expires_at, ip_address):
    try:
        expires_at = int(expires_at)
    except ValueError:
        return False
    if expires_at < int(timezone.now().timestamp()):
        return False
    expected_token = generate_video_token(video_id, quality, expires_at, ip_address)
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

def get_ip_adress(request):
    orwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if orwarded_for:
        ip = orwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
