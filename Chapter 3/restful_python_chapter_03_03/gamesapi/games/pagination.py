"""
Book: Building RESTful Python Web Services
Chapter 3: Improving and adding authentication to an API with Django
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from rest_framework.pagination import LimitOffsetPagination


class LimitOffsetPaginationWithMaxLimit(LimitOffsetPagination):
    max_limit = 10
