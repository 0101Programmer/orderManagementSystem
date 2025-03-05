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