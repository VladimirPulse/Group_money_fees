import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from money_fees.models import Collect, Payment

User = get_user_model()


@pytest.mark.django_db
def test_fill_database_command():
    """
    Тестирует команду заполнения базы данных тестовыми данными.
    Проверяет, что создаются пользователи, сборы и платежи.
    """
    # Вызываем команду
    call_command("fill_db")
    # Проверяем, что созданы пользователи
    users = User.objects.all()
    assert (
        users.count() == 5
    ), f"Ожидалось 5 пользователей, но создано {users.count()}"
    # Проверяем, что созданы сборы
    collects = Collect.objects.all()
    assert (
        collects.count() >= 10
    ), f"Ожидалось минимум 10 сборов, но создано {collects.count()}"
    # Проверяем, что созданы платежи
    payments = Payment.objects.all()
    assert (
        payments.count() == 1000
    ), f"Ожидалось 1000 платежей, но создано {payments.count()}"
    # Дополнительные проверки (например, суммы платежей)
    for payment in payments:
        assert (
            100 <= payment.amount <= 1000
        ), f"Сумма платежа {payment.amount} вне диапазона 100-1000"
    # Проверяем, что у сборов есть авторы из созданных пользователей
    for collect in collects:
        assert (
            collect.author in users
        ), f"Автор сбора {collect.author} не из списка пользователей"


@pytest.mark.django_db
def test_fill_database_command_no_initial_data():
    """
    Тестирует поведение команды, если изначально нет доступных сборов.
    Проверяет, что создаются новые сборы, если доступных нет.
    """
    # Удаляем все сборы, чтобы проверить создание новых
    Collect.objects.all().delete()
    # Вызываем команду
    call_command("fill_db")
    # Проверяем, что созданы новые сборы
    collects = Collect.objects.all()
    assert (
        collects.count() >= 5
    ), f"Ожидалось минимум 5 новых сборов, но создано {collects.count()}"
