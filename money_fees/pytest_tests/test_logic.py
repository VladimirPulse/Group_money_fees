import time

import pytest

from money_fees.models import Collect, Payment
from money_fees.pytest_tests.constans import URL_COLLECT, URL_PAY


@pytest.mark.django_db
def test_correct_cashe(admin_client, list_collects):
    """Проверка корректности работы кэша"""
    assert Collect.objects.count() == 10
    start_time = time.time()  # Запоминаем время начала
    admin_client.get("/api/collects/")
    elapsed_time_1 = time.time() - start_time
    # Второй запрос, данные должны загружаться из кэша
    start_time = time.time()  # Запоминаем время начала
    admin_client.get("/api/collects/")
    elapsed_time_2 = time.time() - start_time
    # Проверка, что время ответа на второй
    # запрос < времени ответа на первый запрос
    assert elapsed_time_2 < elapsed_time_1


@pytest.mark.django_db
def test_mail(mailoutbox, author_collect, collectload, payload):
    """Проверка на отправку на почту при создании экземпляров моделей"""
    assert Collect.objects.count() == 0
    assert Payment.objects.count() == 0
    assert len(mailoutbox) == 0
    author_collect.post(URL_COLLECT, data=collectload, format="json")
    author_collect.post(URL_PAY, data=payload, format="json")
    assert len(mailoutbox) == 2
    m = mailoutbox[0]
    assert m.subject == "Подтверждение транзакции"
    assert m.body == "Успешно создан сбор"
    assert m.from_email == "from@example.com"
    assert m.to == [author_collect.handler._force_user.email]
    m_2 = mailoutbox[1]
    assert m_2.subject == "Подтверждение транзакции"
    assert m_2.body == "Успешно создана инвестиция"
    assert m_2.from_email == "from@example.com"
    assert m_2.to == [author_collect.handler._force_user.email]


@pytest.mark.django_db
def test_bad_mail(mailoutbox, author_collect):
    """Проверка, что нет отправки на почту при отсутсвии создания экземпляра"""
    assert Collect.objects.count() == 0
    assert Payment.objects.count() == 0
    assert len(mailoutbox) == 0
    author_collect.post(URL_COLLECT, format="json")
    author_collect.post(URL_PAY, format="json")
    assert len(mailoutbox) == 0
