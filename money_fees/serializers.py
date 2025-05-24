import base64
import datetime as dt
import logging

from django.core.files.base import ContentFile
from django.core.mail import send_mail
from rest_framework import serializers

from group_money_fees.settings import DEFAULT_FROM_EMAIL

from .models import Collect, Payment, User

logger = logging.getLogger(__name__)


class Base64ImageField(serializers.ImageField):
    """Класс обработки картинок."""

    def to_internal_value(self, data):
        """Обработка картинок."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            if ext != "jpeg":
                ext = "jpeg"
            filename = f"image.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)


class PaymentSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ["amount", "created_at", "collec_fees"]

    def get_created_at(self, obj):
        date_time = obj.created_at
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def create(self, validated_data):
        user = self.context["request"].user
        collec_fees = validated_data.pop("collec_fees")
        if collec_fees.end_date:
            raise serializers.ValidationError(
                f'Выберите другой сбор. Этот сбор завершен {
                    collec_fees.end_date.strftime("%Y-%m-%d %H:%M:%S")
                }'
            )
        collec_fees.curr_sum_fees += validated_data["amount"]
        if collec_fees.sum_fees <= collec_fees.curr_sum_fees:
            collec_fees.end_date = dt.datetime.now()
        data_pay = Payment.objects.filter(user=user, collec_fees=collec_fees)
        if not data_pay.exists():
            collec_fees.donors_count += 1
        collec_fees.save()
        payment = Payment.objects.create(
            user=user, collec_fees=collec_fees, **validated_data
        )
        logger.info(f"Отправка письма пользователю: {user.email}")
        send_mail(
            subject="Подтверждение транзакции",
            message="Успешно создана инвестиция",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[f"{user.email}"],
            fail_silently=True,
        )
        return payment


class PaymentCollectSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ["user", "amount", "created_at"]

    def get_created_at(self, obj):
        date_time = obj.created_at
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def to_representation(self, instance):
        """Представление."""
        data = super().to_representation(instance)
        data["user"] = User.objects.get(id=data["user"]).username
        return data


class CollectSerializer(serializers.ModelSerializer):
    end_date = serializers.SerializerMethodField()
    fees = PaymentCollectSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Collect
        fields = [
            "author",
            "title",
            "slug",
            "description",
            "sum_fees",
            "curr_sum_fees",
            "donors_count",
            "image",
            "fees",
            "end_date",
        ]

    def get_end_date(self, obj):
        if obj.end_date:
            date_time = obj.end_date
            return date_time.strftime("%Y-%m-%d %H:%M:%S")
        return obj.end_date

    def to_representation(self, instance):
        """Представление."""
        data = super().to_representation(instance)
        return data
