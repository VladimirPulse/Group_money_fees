import json
from http import HTTPStatus

import pytest

from money_fees.pytest_tests.constans import (URL_ADMIN, URL_COLLECT,
                                              URL_CREAT_USER, URL_PAY,
                                              URL_TOKEN)


def test_access_admin_area_auth(admin_client, client, user_data):
    """Проверка на доступ к админке и аутентификации"""
    response = admin_client.get(URL_ADMIN)
    assert response.status_code == HTTPStatus.OK
    response = client.post(URL_CREAT_USER, user_data)
    assert response.status_code == HTTPStatus.CREATED
    response = client.post(URL_TOKEN, user_data)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_access_urls_collect_pay(client, user_data):
    """Проверка на доступ к url сбора и инвестиции"""
    client.post(URL_CREAT_USER, user_data)
    response_token = client.post(URL_TOKEN, user_data)
    assert response_token.status_code == HTTPStatus.OK
    # Преобразование строки JSON в словарь
    response_data = json.loads(response_token.text)
    # Извлечение токенов
    access_token = response_data.get("access")
    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {access_token}",
    }
    response_collect = client.get(URL_COLLECT, **headers)
    assert response_collect.status_code == HTTPStatus.OK
    response_pay = client.get(URL_PAY, **headers)
    assert response_pay.status_code == HTTPStatus.OK
