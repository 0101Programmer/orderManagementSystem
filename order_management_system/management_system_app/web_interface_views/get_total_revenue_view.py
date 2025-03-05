from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Sum

from ..models import Order


class GetTotalRevenue(View):
    def get(self, request):
        # Фильтруем заказы со статусом "оплачено"
        paid_orders = Order.objects.filter(status='оплачено')

        # Считаем сумму по столбцу total_price
        total_revenue = paid_orders.aggregate(total_sum=Sum('total_price'))['total_sum']

        # Если заказов нет, total_revenue будет 0
        if total_revenue is None:
            total_revenue = 0

        return render(request, 'orders_crud_web_inter/get_total_revenue.html',
                      {'header': 'Расчет выручки за смену',
                       'title': 'Order Management System',
                       'total_revenue': total_revenue})