from django.db.models import Sum
from django.http import JsonResponse
from rest_framework import generics

from ..models import Order


class OrderAPIGetTotalRevenue(generics.GenericAPIView):
    def get(self, request):
        # Фильтруем заказы со статусом "оплачено"
        paid_orders = Order.objects.filter(status='оплачено')

        # Считаем сумму по столбцу total_price
        total_revenue = paid_orders.aggregate(total_sum=Sum('total_price'))['total_sum']

        # Если заказов нет, total_revenue будет 0
        if total_revenue is None:
            total_revenue = 0

        # Возвращаем JSON ответ
        return JsonResponse({'total_revenue': total_revenue})