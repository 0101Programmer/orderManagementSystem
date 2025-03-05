from django.shortcuts import render, redirect
from django.views import View

from ..forms import GetOrderForm
from ..models import Order


class GetAllOrders(View):
    def get(self, request):
        orders = Order.objects.all()  # Получаем все заказы
        return render(request, 'orders_crud_web_inter/get_all_orders.html',
                      {'header': 'Отображение всех заказов',
                       'title': 'Order Management System',
                       'orders': orders})