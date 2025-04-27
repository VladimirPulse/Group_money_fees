import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from money_fees.models import Collect
from money_fees.serializers import PaymentSerializer

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        # Создание нескольких пользователей
        users = [User.objects.create(username=f'user{i}') for i in range(1, 6)]

        # Создание тестовых групповых сборов
        collect_list = []
        for i in range(10):
            collect = Collect.objects.create(
                author=random.choice(users),
                title=f'Сбор {i}',
                slug=random.choice(['birthday', 'wedding']),
                description=f'Тестовое описание {i}',
                sum_fees=random.randint(1000, 5000),
            )
            collect_list.append(collect)

        # Функция для получения доступных сборов
        def get_available_collects():
            list_of_collects = list(Collect.objects.all())
            available_collects = [
                collect for collect in
                list_of_collects if collect.end_date is None
            ]
            if not available_collects:
                # Если нет доступных сборов, создаем новые
                for i in range(5):  # Создаем 5 новых сборов
                    collect = Collect.objects.create(
                        author=random.choice(users),
                        title=f'Сбор новый {i}',
                        slug=random.choice(['birthday', 'wedding']),
                        description=f'Тестовое описание нового {i}',
                        sum_fees=random.randint(1000, 5000),
                    )
                    available_collects.append(collect)
                # После создания новых сборов, снова фильтруем доступные
                # available_collects = collect_list
            return available_collects

        # Создание платежей
        for i in range(1000):
            available_collects = get_available_collects()
            selected_collect = random.choice(available_collects)
            payment_data = {
                'user': random.choice(users).id,
                'amount': random.randint(100, 1000),
                'collec_fees': selected_collect.id
            }
            serializer = PaymentSerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Ошибка при создании платежа: {serializer.errors}'))
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))
