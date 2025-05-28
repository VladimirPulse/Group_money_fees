import os
import shutil
import time

import docker
import pytest
from django.conf import settings
from rest_framework.test import APIClient

from money_fees.models import Collect


@pytest.fixture(autouse=True)
def cleanup_media():
    yield
    media_path = os.path.join(settings.MEDIA_ROOT, "images")
    if os.path.exists(media_path):
        shutil.rmtree(media_path)


@pytest.fixture
def author_collect(client, django_user_model):
    user = django_user_model.objects.create(
        username="user", email="test_user@example.com"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user_investor(client, django_user_model):
    user = django_user_model.objects.create(
        username="user2", email="test_user2@example.com"
    )
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
    return {"amount": 500, "collec_fees": 1}


@pytest.fixture
def list_collects(author_collect):
    for i in range(10):
        Collect.objects.create(
            author=author_collect.handler._force_user,
            title=f"Сбор {i}",
            slug="test-collect",
            description="This is a test collect.",
            sum_fees=100,
        )


@pytest.fixture(scope="session")
def docker_container():
    client = docker.from_env()
    container = client.containers.run(
        "fees_backend", detach=True, ports={"8000/tcp": 8000}
    )
    # Ждем, пока контейнер не перейдет в состояние "running"
    timeout = 30
    start_time = time.time()
    while container.status != "running":
        container.reload()
        if time.time() - start_time > timeout:
            raise TimeoutError(
                "Контейнер не запустился в течение заданного времени"
            )
        time.sleep(1)
    yield container
    container.stop()
    container.remove()
