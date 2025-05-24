from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework import viewsets

from group_money_fees.settings import DEFAULT_FROM_EMAIL

from .models import Collect, Payment
from .serializers import CollectSerializer, PaymentSerializer


class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer

    def create(self, request, *args, **kwargs):
        request.data["author"] = request.user.id
        response = super().create(request, *args, **kwargs)
        send_mail(
            subject="Подтверждение транзакции",
            message="Успешно создан сбор",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[f"{request.user.email}"],
            fail_silently=True,
        )
        cache.clear()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.clear()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.clear()
        return response


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
