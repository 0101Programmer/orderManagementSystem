from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import UpdateOrderItemsForm
from ..models import Order


class UpdateOrderItems(View):
    def get(self, request, pk):
        # Получаем заказ по ID или возвращаем 404, если заказ не найден
        order = get_object_or_404(Order, id=pk)

        # Передаем заказ в форму для предзаполнения данных
        form = UpdateOrderItemsForm(instance=order)

        return render(request, 'orders_crud_web_inter/update_order_items.html',
                      {'header': 'Изменение содержимого заказа',
                       'title': 'Order Management System',
                       'form': form, 'order': order})

    def post(self, request, pk):
        # Получаем заказ по ID или возвращаем 404, если заказ не найден
        order = get_object_or_404(Order, id=pk)

        # Передаем данные POST и экземпляр заказа в форму
        form = UpdateOrderItemsForm(request.POST, instance=order)
        if form.is_valid():
            # Сохраняем изменения в заказе
            form.save()
            return redirect('update_order_items', pk=order.id)  # Перенаправляем на ту же страницу

        return render(request, 'orders_crud_web_inter/update_order_items.html',
                      {'header': 'Изменение содержимого заказа',
                       'title': 'Order Management System',
                       'form': form, 'order': order})