import time
from http import HTTPStatus

import requests


def test_container_is_running(docker_container):
    # import pdb;pdb.set_trace()
    assert docker_container.status == "running"


def test_service_response(docker_container):
    timeout = 30
    start_time = time.time()
    while True:
        try:
            response = requests.get("http://localhost:8000/api/", timeout=5)
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                break
        except requests.exceptions.RequestException:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    "Сервис не стал доступен в течение заданного времени"
                )
            time.sleep(1)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
