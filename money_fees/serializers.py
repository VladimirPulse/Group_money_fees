import base64
import datetime as dt

from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Collect, Payment, User


class Base64ImageField(serializers.ImageField):
    """Класс обработки картинок."""

    def to_internal_value(self, data):
        """Обработка картинок."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            if ext != 'jpeg':
                ext = 'jpeg'
            filename = f'image.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)


class PaymentSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_created_at(self, obj):
        date_time = obj.created_at
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def create(self, validated_data):
        collec_fees = validated_data.pop('collec_fees')
        collec_fees.curr_sum_fees += validated_data['amount']
        if collec_fees.sum_fees <= collec_fees.curr_sum_fees:
            collec_fees.end_date = dt.datetime.now()
        data_pay = Payment.objects.filter(
            user=validated_data['user'],
            collec_fees=collec_fees
        )
        if not data_pay.exists():
            collec_fees.donors_count += 1
        collec_fees.save()
        payment = Payment.objects.create(
            collec_fees=collec_fees, **validated_data)
        return payment


class PaymentCollectSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'user',
            'amount',
            'created_at'
        ]

    def get_created_at(self, obj):
        date_time = obj.created_at
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def to_representation(self, instance):
        """Представление."""
        data = super().to_representation(instance)
        data['user'] = User.objects.get(
            id=data['user']
        ).username
        return data


class CollectSerializer(serializers.ModelSerializer):
    end_date = serializers.SerializerMethodField()
    fees = PaymentCollectSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Collect
        fields = [
            'author',
            'title',
            'slug',
            'description',
            'sum_fees',
            'curr_sum_fees',
            'donors_count',
            'image',
            'fees',
            'end_date'
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
