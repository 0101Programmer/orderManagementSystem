from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import DeleteOrderForm
from ..models import Order

class DeleteOrder(View):
    def get(self, request):
        form = DeleteOrderForm()
        return render(request, 'orders_crud_web_inter/delete_order.html',
                      {'header': 'Удаление заказа',
                       'title': 'Order Management System',
                       'form': form})

    def post(self, request):
        form = DeleteOrderForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']  # Получаем ID заказа
            order = get_object_or_404(Order, id=order_id)  # Находим заказ
            order.delete()  # Удаляем заказ
            return redirect('/crud/delete_order')
        return render(request, 'orders_crud_web_inter/delete_order.html',
                      {'header': 'Удаление заказа',
                       'title': 'Order Management System',
                       'form': form})