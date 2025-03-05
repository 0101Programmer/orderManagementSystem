from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import UpdateOrderStatusForm
from ..models import Order


class UpdateOrderStatus(View):
    def get(self, request):
        form = UpdateOrderStatusForm()
        return render(request, 'orders_crud_web_inter/update_order_status.html',
                      {'header': 'Изменение статуса заказа',
                       'title': 'Order Management System',
                       'form': form})

    def post(self, request):
        form = UpdateOrderStatusForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']  # Получаем ID заказа
            status = form.cleaned_data['status']  # Получаем новый статус

            # Находим заказ и обновляем его статус
            order = get_object_or_404(Order, id=order_id)
            if order.status != status:
                Order.objects.filter(id=order_id).update(status=status)
            return redirect('update_order_status')
        return render(request, 'orders_crud_web_inter/update_order_status.html',
                      {'header': 'Изменение статуса заказа',
                       'title': 'Order Management System',
                       'form': form})