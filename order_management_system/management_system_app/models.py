import uuid

from django.db import models

# Create your models here.

class Order(models.Model):
    # Поле id создается автоматически
    table_number = models.IntegerField(help_text='Номер стола, например: 1, 2, 3...')
    items = models.JSONField(help_text='Список заказанных блюд с ценами, например: '
                                       '[{"position": "Картофель фри", "price": 199.99}, '
                                       '{"position": "Шашлык", "price": 454.99}, ...]')
    total_price = models.FloatField(default=0.0, help_text=
    'Общая стоимость заказа, которая вычисляется автоматически.'
    'Чтобы избежать ошибок, если поле не будет заполнено, устанавливаем дефолтное значение')
    status = models.CharField(max_length=50,
                              help_text='Статус заказа: “в ожидании”, “готово”, “оплачено”')


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
                        self.total_price += float(order_dict['price'])
            else:
                self.total_price = 0  # Если items пуст, сумма равна 0

        # Вызываем оригинальный метод save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Стол номер {self.table_number}; заказы: {self.items}'