from django.shortcuts import render, redirect
from django.views import View

from ..forms import GetOrderForm
from ..models import Order


class GetOrder(View):
    def get(self, request):
        form = GetOrderForm(request.GET or None)
        # Передаем None, если request.GET пуст, чтобы первичная загрузка страницы не вызывала ошибок

        orders = None  # Инициализируем переменную для найденных заказов

        # Проверяем, есть ли данные в request.GET
        if request.GET and form.is_valid():
            table_number = form.cleaned_data.get('table_number')  # Получаем номер стола
            status = form.cleaned_data.get('status')  # Получаем статус заказа

            # Выполняем поиск заказов
            filters = {}
            if table_number:
                filters['table_number'] = table_number
            if status:
                filters['status'] = status

            orders = Order.objects.filter(**filters)  # Получаем заказы по необходимому фильтру

        return render(request, 'orders_crud_web_inter/get_order.html',
                      {'header': 'Поиск заказа',
                       'title': 'Order Management System',
                       'form': form,
                       'orders': orders})