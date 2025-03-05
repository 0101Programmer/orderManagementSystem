from django.shortcuts import render, redirect
from django.views import View

from ..forms import AddOrderForm


class AddOrder(View):
    def get(self, request):
        form = AddOrderForm()
        return render(request, 'orders_crud_web_inter/add_order.html',
                      {'header': 'Добавление заказа',
                       'title': 'Order Management System',
                       'form': form})

    def post(self, request):
        form = AddOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud/add_order')
        return render(request, 'orders_crud_web_inter/add_order.html',
                      {'header': 'Добавление заказа',
                       'title': 'Order Management System',
                       'form': form})