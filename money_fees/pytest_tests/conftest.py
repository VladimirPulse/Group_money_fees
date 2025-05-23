import pytest
from rest_framework.test import APIClient


@pytest.fixture
def author_collect(client, django_user_model):
    user = django_user_model.objects.create(username="user")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user_data():
    return {"username": "testuser", "password": "testpassword"}


@pytest.fixture
def collectload():
    return {
        "title": "Тестовый сбор",
        "description": "Описание тестового сбора",
        "sum_fees": 1000,
    }


@pytest.fixture
def payload():
    return {"amount": 1000, "collec_fees": 1}
