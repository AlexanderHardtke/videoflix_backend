from datetime import timezone
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination, BasePagination
from rest_framework.response import Response
from collections import defaultdict
import os
from django.conf import settings


class TypeBasedPagination(PageNumberPagination):
    page_size = 8
    page_size_per_type = 8
    page_size_query_param = 'list_size'
    max_page_size = 99
    page_query_param = 'list'
    video_types = [x for x in os.environ.get('VIDEO_TYPES').split(',') if x]

    # def paginate_queryset(self, queryset, request, view=None):
    #     keks = os.environ.get('VIDEO_TYPES', '')
    #     print(keks)
    #     self.request = request
    #     self.page = int(request.query_params.get(self.page_query_param, 1))

    #     grouped = defaultdict(list)
    #     for video in queryset:
    #         grouped[video.type].append(video)

    #     # Pro Typ nur max `page_size_per_type` Elemente holen
    #     limited_per_type = []
    #     for videos in grouped.values():
    #         limited_per_type.extend(islice(videos, self.page_size_per_type))

    #     # Gesamtliste paginieren (z.B. page 1 = erste 20 Videos, page 2 = nächste 20 ...)
    #     self.total_items = len(limited_per_type)
    #     self.page_size = self.page_size_per_type * len(grouped)

    #     start = (self.page - 1) * self.page_size
    #     end = start + self.page_size

    #     self.paginated_items = limited_per_type[start:end]
    #     return self.paginated_items

    # def get_paginated_response(self, data):
    #     return Response({
    #         'count': self.total_items,
    #         'page': self.page,
    #         'next': self._get_next_link(),
    #         'previous': self._get_prev_link(),
    #         'results': data
    #     })

    # def _get_next_link(self):
    #     if self.page * self.page_size >= self.total_items:
    #         return None
    #     url = self.request.build_absolute_uri()
    #     return self._replace_query_param(url, self.page_query_param, self.page + 1)

    # def _get_prev_link(self):
    #     if self.page == 1:
    #         return None
    #     url = self.request.build_absolute_uri()
    #     return self._replace_query_param(url, self.page_query_param, self.page - 1)

    # def _replace_query_param(self, url, key, value):
    #     from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

    #     parsed = urlparse(url)
    #     query = parse_qs(parsed.query)
    #     query[key] = [str(value)]
    #     new_query = urlencode(query, doseq=True)
    #     return urlunparse(parsed._replace(query=new_query))

    def get_paginated_response(self, data):

        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
