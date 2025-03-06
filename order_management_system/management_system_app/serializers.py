from rest_framework import serializers
from .models import Order


# сериализатор для передачи модели Order в API представления
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'table_number', 'items', 'total_price', 'status')
        # поля, которые создавать/редактировать вручную нельзя
        read_only_fields = ('id', 'total_price', 'status')

    def validate(self, data):

        # Проверяем, что поле items не пустое
        if not data.get('items'):
            raise serializers.ValidationError({"items": "Заполните поле заказов"})

        # Проверяем, что items является списком
        if not isinstance(data.get('items'), list):
            raise serializers.ValidationError({"items": "Поле items должно быть списком"})

        # Проверяем каждый элемент списка
        for item in data.get('items', []):
            if not isinstance(item, dict):
                raise serializers.ValidationError({'items': 'Каждый элемент списка items должен быть словарём.'})

            # Проверяем, что в словаре ровно два ключа
            if len(item) != 2:
                raise serializers.ValidationError(
                    {'items': 'Каждый элемент items должен содержать ровно два ключа: "position" и "price".'})

            # Проверяем наличие и тип ключей
            if 'position' not in item or not isinstance(item['position'], str):
                raise serializers.ValidationError(
                    {'items': 'Каждый элемент items должен содержать ключ "position", а значение должно быть в строковом представлении.'})
            if 'price' not in item or not isinstance(item['price'], (int, float)):
                raise serializers.ValidationError(
                    {'items': 'Каждый элемент items должен содержать ключ "price", а значение должно быть в числовом представлении.'})

        return data