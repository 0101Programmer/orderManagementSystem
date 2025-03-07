from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from .models import Order
from .drf_views.get_total_revenue_api_view import OrderAPIGetTotalRevenue

# Create your tests here.


# -----------------------------------------------------------------------------
# Тесты для API
# -----------------------------------------------------------------------------
class OrderAPIGetTotalRevenueTestCase(TestCase):
    def setUp(self):
        # Создаем тестовые данные
        Order.objects.create(table_number=1, items=
        [{"position": "Картофель фри", "price": 100}, {"position": "Шашлык", "price": 200}],
                             status='оплачено')
        Order.objects.create(table_number=2, items=
        [{"position": "Картофель фри", "price": 300}, {"position": "Шашлык", "price": 400}],
                             status='оплачено')
        Order.objects.create(table_number=3, items=
        [{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
                             status='готово')
        Order.objects.create(table_number=4, items=
        [{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
                             status='в ожидании')

        # Создаем экземпляр RequestFactory для создания запросов
        self.factory = RequestFactory()

    def test_get_total_revenue(self):
        """
        Проверка суммы, когда есть оплаченные заказы
        """

        # Создаем GET-запрос
        request = self.factory.get('/fake-url/')

        # Вызываем метод get
        response = OrderAPIGetTotalRevenue.as_view()(request)

        # Проверяем, что ответ является JsonResponse
        self.assertIsInstance(response, JsonResponse)

        # Проверяем содержимое ответа
        expected_data = {'total_revenue': 1000}
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_data)

    def test_get_total_revenue_no_paid_orders(self):
        """
        Проверка суммы, когда нет оплаченных заказов
        """

        # Удаляем все оплаченные заказы
        Order.objects.filter(status='оплачено').delete()

        # Создаем GET-запрос
        request = self.factory.get('/fake-url/')

        # Вызываем метод get вашего View
        response = OrderAPIGetTotalRevenue.as_view()(request)

        # Проверяем, что ответ является JsonResponse
        self.assertIsInstance(response, JsonResponse)

        # Проверяем содержимое ответа
        expected_data = {'total_revenue': 0}  # Нет оплаченных заказов
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_data)

# -----------------------------------------------------------------------------
# Тесты для веб-интерфейса
# -----------------------------------------------------------------------------