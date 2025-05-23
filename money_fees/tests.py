import time

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from money_fees.models import Collect

User = get_user_model()


class CollectAPITestCase(APITestCase):
    """Тест на корректность кэширования"""

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        # Получаем токен для этого пользователя
        self.token = str(RefreshToken.for_user(self.user).access_token)
        # Создаем тестовые объекты Collect
        for i in range(10):
            Collect.objects.create(
                author=self.user,
                title=f"Сбор {i}",
                slug="test-collect",
                description="This is a test collect.",
                sum_fees=100,
            )

    def test_collect_cache(self):
        # Устанавливаем заголовок авторизации с токеном
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # Первый запрос, данные должны загружаться из БД
        start_time = time.time()  # Запоминаем время начала
        response1 = self.client.get("/api/collects/")
        elapsed_time_1 = time.time() - start_time
        self.assertEqual(response1.status_code, 200)
        # Второй запрос, данные должны загружаться из кэша
        start_time = time.time()  # Запоминаем время начала
        response2 = self.client.get("/api/collects/")
        elapsed_time_2 = time.time() - start_time
        self.assertEqual(response2.status_code, 200)
        # Проверка, что время ответа на второй
        # запрос < или = времени ответа на первый запрос
        self.assertLessEqual(elapsed_time_2, elapsed_time_1)
