from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from urllib.parse import urlencode
import os


class TypeBasedPagination(PageNumberPagination):
    page_size_per_type = 80
    page_size_query_param = 'list_size'
    max_page_size = 99
    page_query_param = 'list'

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.video_types = [x.strip() for x in os.environ.get('VIDEO_TYPES', '').split(',') if x.strip()]

        self.page_number = int(request.query_params.get(self.page_query_param, 1))
        self.start = (self.page_number - 1) * self.page_size_per_type
        self.end = self.start + self.page_size_per_type

        result = []

        for video_type in self.video_types:
            type_videos = queryset.filter(
                video_type=video_type
            ).order_by('-uploaded_at')[self.start:self.end]

            for video in type_videos:
                video.override_type = video_type
                result.append(video)

        self.count = sum([
            queryset.filter(video_type=vt).count()
            for vt in self.video_types
        ])

        return result

    def get_paginated_response(self, data):
        base_url = self.request.build_absolute_uri().split('?')[0]
        current_params = dict(self.request.query_params)
    
        next_url = None
        if data and len(data) >= self.page_size_per_type * (len(self.video_types) + 1):
            next_params = current_params.copy()
            next_params[self.page_query_param] = [str(self.page_number + 1)]
            next_url = f"{base_url}?{urlencode(next_params, doseq=True)}"
        
        prev_url = None
        if self.page_number > 1:
            prev_params = current_params.copy()
            prev_params[self.page_query_param] = [str(self.page_number - 1)]
            prev_url = f"{base_url}?{urlencode(prev_params, doseq=True)}"
        
        return Response({
            'list': data,
            'count': self.count,
            'list_size': self.page_size_per_type,
            'list_page': self.page_number,
            'next': next_url,
            'previous': prev_url,
        })