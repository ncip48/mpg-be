from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination as drf_PageNumberPagination
from rest_framework.pagination import CursorPagination as drf_CursorPagination
from rest_framework.response import Response


class PageNumberPagination(drf_PageNumberPagination):
    page_query_param = 'page'

    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('current', self.page.number),
            ('previous', self.get_previous_link()),
            ('limit', self.get_page_size(self.request)),
            ('results', data),
        ]))
        
class CursorPagination(drf_CursorPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    cursor_query_param = "cursor"
    ordering = ("-created", "-id")

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            ("limit", self.get_page_size(self.request)),
            ("results", data),
        ]))