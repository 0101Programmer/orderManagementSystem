from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

# дефолтное значение для поля с позициями заказа, которое можно вызвать для каждого экземпляра заказа
def default_items():
    return [{"position": "Блюдо", "price": 199.99}]


class Order(models.Model):
    # Поле id создается автоматически
    table_number = models.IntegerField(help_text='Номер стола, например: 1, 2, 3...',
                                       validators=[MinValueValidator(1,
                                                                     message='Номер стола должен быть больше 0.')])

    items = models.JSONField(default=default_items,
                             help_text='Список заказанных блюд с ценами, например: '
                                       '[{"position": "Картофель фри", "price": 199.99}, '
                                       '{"position": "Шашлык", "price": 454.99}, ...] '
                                       'Обратите внимание, что кавычки должны быть двойными')

    total_price = models.FloatField(help_text=
    'Общая стоимость заказа, которая вычисляется автоматически.')

    status = models.CharField(default='в ожидании', max_length=50,
                              help_text='Статус заказа: “в ожидании”, “готово”, “оплачено”')

    # переопределение метода clean для валидации поля items
    def clean(self):
        super().clean()  # Вызываем родительский метод clean

        # Проверяем, что items является списком
        if not isinstance(self.items, list):
            raise ValidationError({'items': 'Поле items должно быть списком.'})

        # Проверяем каждый элемент списка
        for item in self.items:
            if not isinstance(item, dict):
                raise ValidationError({'items': 'Каждый элемент items должен быть словарём.'})

            # Проверяем, что в словаре ровно два ключа
            if len(item) != 2:
                raise ValidationError({'items': 'Каждый элемент items должен содержать ровно два ключа: "position" и "price".'})

            # Проверяем наличие и тип ключей
            if 'position' not in item or not isinstance(item['position'], str):
                raise ValidationError({'items': 'Каждый элемент items должен содержать ключ "position", а значение должно быть в строковом представлении.'})
            if 'price' not in item or not isinstance(item['price'], (int, float)):
                raise ValidationError({'items': 'Каждый элемент items должен содержать ключ "price", а значение должно быть в числовом представлении.'})


    # переопределение метода save для пересчёта итоговой суммы заказа
    def save(self, *args, **kwargs):
        # Сбрасываем total_price перед вычислением
        self.total_price = 0.0

        # Проверяем, что self.items является списком и не пуст
        if isinstance(self.items, list) and self.items:
            if self.items:
                for order_dict in self.items:
                    # Проверяем, что каждый объект списка является словарем и содержит ключ 'price'
                    if isinstance(order_dict, dict) and 'price' in order_dict:
                        # Вычисляем общую сумму заказа на основе элементов items
                        self.total_price += round(float(order_dict['price']), 2)
            else:
                self.total_price = 0  # Если items пуст, сумма равна 0

        # Вызываем оригинальный метод save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Стол номер {self.table_number}; заказы: {self.items}'