import copy
import time
from http import HTTPStatus

import pytest

from money_fees.models import Collect, Payment, User
from money_fees.pytest_tests.constans import (FIELDS_FEES, URL_ADMIN_COLLECT,
                                              URL_ADMIN_PAY, URL_COLLECT,
                                              URL_PAY)
from money_fees.serializers import CollectSerializer


@pytest.mark.django_db
def test_correct_cache(admin_client, list_collects):
    """Тестирование функциональности кэша."""
    assert Collect.objects.count() == 10
    # Измеряем время ответа на первый запрос
    start_time = time.time()
    admin_client.get(URL_COLLECT)
    elapsed_time_1 = time.time() - start_time
    # Измеряем время ответа на второй запрос (должен использовать кэш)
    start_time = time.time()
    admin_client.get(URL_COLLECT)
    elapsed_time_2 = time.time() - start_time
    # Проверяем, что время ответа на второй запрос меньше, чем на первый
    assert elapsed_time_2 < elapsed_time_1


@pytest.mark.django_db
def test_mail(mailoutbox, author_collect, collectload, payload):
    """Тестирование отправки писем при создании моделей."""
    assert not Collect.objects.exists()
    assert not Payment.objects.exists()
    assert len(mailoutbox) == 0
    # Создаем сбор и платеж
    author_collect.post(URL_COLLECT, data=collectload, format="json")
    author_collect.post(URL_PAY, data=payload, format="json")
    # Проверяем, что было отправлено два письма
    assert len(mailoutbox) == 2
    expected_subject = "Подтверждение транзакции"
    expected_from_email = "from@example.com"
    expected_recipient = [author_collect.handler._force_user.email]
    for m in mailoutbox:
        assert m.subject == expected_subject
        assert m.from_email == expected_from_email
        assert m.to == expected_recipient
        assert m.body in ["Успешно создан сбор", "Успешно создана инвестиция"]


@pytest.mark.django_db
def test_logic_invest(author_collect, user_investor, collectload, payload):
    """Тестирование логики инвестирования."""
    assert Collect.objects.count() == 0
    assert Payment.objects.count() == 0
    # Создаем сбор
    author_collect.post(URL_COLLECT, data=collectload, format="json")
    assert Collect.objects.count() == 1
    collect = Collect.objects.get()
    # Проверяем начальные значения
    assert collect.curr_sum_fees == 0
    assert collect.donors_count == 0
    assert collect.end_date is None
    # Инвестирование первым пользователем
    author_collect.post(URL_PAY, data=payload, format="json")
    # Инвестирование вторым пользователем
    payload_2 = copy.deepcopy(payload)
    payload_2["amount"] = 1
    user_investor.post(URL_PAY, data=payload_2, format="json")
    # Повторное инвестирование первым пользователем
    author_collect.post(URL_PAY, data=payload, format="json")
    # Проверяем итоговые значения
    collect.refresh_from_db()
    assert collect.curr_sum_fees == 2 * payload["amount"] + payload_2["amount"]
    assert collect.donors_count == 2
    assert collect.end_date is not None
    # Проверяем сериализацию инвестиций
    serializer = CollectSerializer(collect)
    fees_data = serializer.data["fees"]
    assert isinstance(fees_data, list), "Инвестиции должны быть перечислены."
    assert (
        len(fees_data) == 3
    ), "Инвестиций не может быть больше, чем инвесторов."
    for fee in fees_data:
        assert (
            set(fee.keys()) == FIELDS_FEES
        ), "Инвестиции должны содержать поля user, amount и created_at."
    # Проверяем количество платежей
    assert Payment.objects.count() == 3
    # Попытка инвестировать в закрытый сбор
    response = author_collect.post(URL_PAY, data=payload, format="json")
    assert response.status_code == HTTPStatus.BAD_REQUEST  # Ожидаем ошибку
    # Количество платежей не должно увеличиться
    assert Payment.objects.count() == 3


@pytest.mark.django_db
def test_create_obj_admin(admin_client, collectload, payload):
    """Тестирование создания объектов через админку."""
    assert User.objects.count() == 1
    assert Collect.objects.count() == 0
    assert Payment.objects.count() == 0
    # Создаем сбор
    collectload["author"] = 1
    response = admin_client.post(
        URL_ADMIN_COLLECT, data=collectload, format="json"
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Collect.objects.count() == 1
    collect = Collect.objects.get()
    # Проверка начальных значений
    assert collect.curr_sum_fees == 0
    assert collect.donors_count == 0
    assert collect.end_date is None
    # Создаем платеж
    payload["user"] = 1
    response_pay = admin_client.post(
        URL_ADMIN_PAY, data=payload, format="json"
    )
    assert response_pay.status_code == HTTPStatus.FOUND
    payment = Payment.objects.get()
    assert payment.user == User.objects.get(id=1)
    assert payment.amount == payload["amount"]
    assert payment.created_at
    assert payment.collec_fees.id == payload["collec_fees"]
    # Проверка обновления сведений в сборе
    collect.refresh_from_db()
    assert collect.curr_sum_fees == payload["amount"]
    assert collect.donors_count == 1
    assert Payment.objects.count() == 1
