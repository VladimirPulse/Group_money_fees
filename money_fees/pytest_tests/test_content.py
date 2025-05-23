import pytest

from money_fees.models import Collect, Payment
from money_fees.pytest_tests.constans import (DEFAULT_SLUG, IMAGE, URL_COLLECT,
                                              URL_PAY)


@pytest.mark.django_db
def test_creat_collect_not_image(author_collect, collectload):
    """Проверка на создание сбора без поля картинки"""
    assert Collect.objects.count() == 0
    author_collect.post(URL_COLLECT, data=collectload, format="json")
    collect = Collect.objects.get()
    assert collect.author == author_collect.handler._force_user
    assert collect.title == collectload["title"]
    assert collect.slug == DEFAULT_SLUG
    assert collect.description == collectload["description"]
    assert collect.sum_fees == collectload["sum_fees"]
    assert collect.curr_sum_fees == 0
    assert collect.donors_count == 0
    assert not collect.image
    assert collect.end_date is None


@pytest.mark.django_db
def test_creat_collect_image(author_collect, collectload):
    """Проверка на создание сбора с изображением"""
    assert Collect.objects.count() == 0
    collectload["image"] = IMAGE
    author_collect.post(URL_COLLECT, data=collectload, format="json")
    assert Collect.objects.count() == 1
    collect = Collect.objects.get()
    assert collect.image.name.startswith("images/")


@pytest.mark.django_db
def test_creat_pay(author_collect, collectload, payload):
    """Проверка на создание инвестиции"""
    assert Collect.objects.count() == 0
    assert Payment.objects.count() == 0
    author_collect.post(URL_COLLECT, data=collectload, format="json")
    author_collect.post(URL_PAY, data=payload, format="json")
    assert Payment.objects.count() == 1
    pay = Payment.objects.get()
    assert pay.user == author_collect.handler._force_user
    assert pay.amount == payload["amount"]
    assert pay.created_at
    assert pay.collec_fees.id == payload["collec_fees"]
