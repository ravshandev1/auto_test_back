from rest_framework import serializers
from .models import TelegramUser, Information, Rate, PaymentType


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['name', 'phone_number', 'telegram_id', 'lang']


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = ['image', 'text_ru', 'text_uz']

    image = serializers.CharField(source='image.path')
