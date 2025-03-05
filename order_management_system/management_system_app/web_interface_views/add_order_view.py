from django.shortcuts import render
from django.views import View


class AddOrder(View):
    def get(self, request):
        return render(request, 'orders_crud_web_inter/add_order.html',
                      {'header': 'Добавление заказа',
                       'title': 'Order Management System'})

    def post(self, request):
        pass