from django.urls import path

from .web_interface_views.add_order_view import AddOrder
from .web_interface_views.delete_order_view import DeleteOrder


urlpatterns = [
    # urls для CRUD запросов в БД с помощью веб интерфейса
    path('crud/add_order', AddOrder.as_view(), name='add_order'),
    path('crud/delete_order', DeleteOrder.as_view(), name='delete_order'),
]