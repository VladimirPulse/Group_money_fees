import json

from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class CacheMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        """Проверка перед обработкой запроса и сохранение в кэш."""
        if request.method == 'GET' and response.status_code == 200:
            cache_key = self.get_cache_key(request)
            cache.set(cache_key, response.content, timeout=60 * 15)
        return response

    def process_request(self, request):
        """Проверяем кэш."""
        if request.method == 'GET':
            cache_key = self.get_cache_key(request)
            cached_response = cache.get(cache_key)
            if cached_response:
                # Десериализуем байтовые данные в словарь
                return JsonResponse(json.loads(cached_response), safe=False)

    def get_cache_key(self, request):
        """Формирует уникальный ключ для кэша."""
        return f"{request.path}?{request.META['QUERY_STRING']}"
