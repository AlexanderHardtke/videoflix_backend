from collections import defaultdict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from videoflix_db.models import Video


class TypeBasedPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'list_size'
    max_page_size = 99
    page_query_param = 'list'

    def __init__(self):
        super().__init__()
        self.video_types = [choice[0] for choice in Video.VIDEO_TYPE_CHOICES]

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.page_number = int(request.query_params.get(self.page_query_param, 1))
        self.type_count = {}
        self.type_results = defaultdict(list)
        self.total_count = 0

        for video_type in self.video_types:
            total, page_videos = self.load_videos_by_type(queryset, video_type)
            self.type_count[video_type] = total
            self.total_count += total
            self.type_results[video_type] = list(page_videos)

        flat_result = [video for vt in self.video_types for video in self.type_results[vt]]
        return flat_result
    
    def load_videos_by_type(self, queryset, video_type):
        videos = queryset.model.objects.filter(video_type=video_type).order_by('-uploaded_at')
        total = videos.count()
        start_index = (self.page_number - 1) * self.page_size
        end_index = start_index + self.page_size
        page_videos = videos[start_index:end_index]
        return total, list(page_videos)

    def has_next_page(self):
        return any(
            self.page_number * self.page_size < total
            for total in self.type_count.values()
        )

    def get_next_link(self):
        if not self.has_next_page():
            return None
        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, self.page_number + 1)

    def get_paginated_response(self, data):
        return Response({
            'list': data,
            'count': self.total_count,
            'list_size': self.page_size,
            'list_page': self.page_number,
            'has_next': self.has_next_page(),
            'next': self.get_next_link(),
        })