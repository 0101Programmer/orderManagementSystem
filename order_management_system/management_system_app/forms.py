
from django import forms
from django.core.exceptions import ValidationError

from .models import Order

# форма для добавления заказа через веб-интерфейс
class AddOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number', 'items']
        labels = {
            'table_number': 'Номер стола',
            'items': 'Список заказанных блюд с ценами'
        }
        widgets = {
            'table_number': forms.NumberInput(attrs={'placeholder': 1,
                                                     'class': 'form-control'}),
            'items': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'Введите данные в формате JSON, например: [{"position": "Блюдо", "price": 199.99}]',
                'class': 'form-control',
            }),
        }

# форма для удаления заказа через веб-интерфейс
class DeleteOrderForm(forms.Form):
    order_id = forms.ChoiceField(label="ID заказа")

    # Переопределяем метод, чтобы динамически заполнить список вариантов
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем все заказы из базы данных
        orders = Order.objects.all()
        # Создаем список вариантов для выпадающего списка
        self.fields['order_id'].choices = [(order.id, f'{order.id}') for order in orders]

# форма для просмотра заказа через веб-интерфейс
class GetOrderForm(forms.Form):
    table_number = forms.IntegerField(label='Номер стола', required=False)
    status = forms.CharField(label='Статус заказа', required=False)

    # Проверка того, что поиск заказов происходит по номеру стола или статусу
    def clean(self):
        cleaned_data = super().clean()  # Получаем очищенные данные
        table_number = cleaned_data.get('table_number')
        status = cleaned_data.get('status')

        # Проверяем, что заполнено только одно поле
        if table_number and status:
            raise ValidationError('Заполните только одно поле: либо номер стола, либо статус заказа.')
        if not table_number and not status:
            raise ValidationError('Заполните хотя бы одно поле: номер стола или статус заказа.')

        return cleaned_data

# форма для изменения статуса заказа через веб-интерфейс
class UpdateOrderStatusForm(forms.Form):
    order_id = forms.ChoiceField(label="ID заказа")
    status = forms.ChoiceField(
        label="Статус заказа",
        choices=[
            ('в ожидании', 'В ожидании'),
            ('готово', 'Готово'),
            ('оплачено', 'Оплачено'),
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем все заказы из базы данных
        orders = Order.objects.all()
        # Создаем список вариантов для выпадающего списка
        self.fields['order_id'].choices = [(order.id, f'{order.id}') for order in orders]
