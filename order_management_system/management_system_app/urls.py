from django.urls import path

from .drf_views.order_views import OrderAPIList, OrderAPICreate, OrderAPIUpdateStatus, OrderAPIDelete
from .web_interface_views.add_order_view import AddOrder
from .web_interface_views.delete_order_view import DeleteOrder
from .web_interface_views.get_all_orders_view import GetAllOrders
from .web_interface_views.get_order_view import GetOrder
from .web_interface_views.get_total_revenue_view import GetTotalRevenue
from .web_interface_views.update_order_status_view import UpdateOrderStatus

urlpatterns = [
    # urls для CRUD запросов в БД с помощью веб интерфейса
    path('crud/add_order', AddOrder.as_view(), name='add_order'),
    path('crud/delete_order', DeleteOrder.as_view(), name='delete_order'),
    path('crud/get_order', GetOrder.as_view(), name='get_order'),
    path('crud/get_all_orders', GetAllOrders.as_view(), name='get_all_orders'),
    path('crud/update_order_status', UpdateOrderStatus.as_view(), name='update_order_status'),
    path('crud/get_total_revenue', GetTotalRevenue.as_view(), name='get_total_revenue'),

    # urls для API
    path('api/v1/order_create/', OrderAPICreate.as_view(), name='order_create'),

    # следующий запрос возвращает как все заказы, так и по параметрам status и table_number,
    # если они переданы в запрос, например:
    # api/v1/order_list/?table_number=7, или api/v1/order_list/?status=в%20ожидании
    path('api/v1/order_list/', OrderAPIList.as_view(), name='order_list'),

    path('api/v1/order_update_status/<int:pk>/', OrderAPIUpdateStatus.as_view(), name='order_update_status'),
    path('api/v1/order_delete/<int:pk>/', OrderAPIDelete.as_view(), name='order_delete'),
]