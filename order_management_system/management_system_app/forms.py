from django import forms

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

# форма для удаления заказа через веб-интерфейс
class DeleteOrderForm(forms.Form):
    order_id = forms.ChoiceField(label="ID заказа")

    # Переопределяем метод, чтобы динамически заполнить список вариантов
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем все заказы из базы данных
        orders = Order.objects.all()
        # Создаем список вариантов для выпадающего списка
        self.fields['order_id'].choices = [(order.id, f'ID №{order.id}') for order in orders]