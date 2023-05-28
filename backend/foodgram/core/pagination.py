from rest_framework.pagination import PageNumberPagination


class FGPagination(PageNumberPagination):
    page_size_query_param = 'limit'
