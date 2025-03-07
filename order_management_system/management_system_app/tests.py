from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Order
from .drf_views.get_total_revenue_api_view import OrderAPIGetTotalRevenue
from django.urls import reverse

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

        # Получаем реальный URL по имени маршрута
        url = reverse('get_total_revenue_by_api')


        # Создаем GET-запрос
        request = self.factory.get(url)

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

        url = reverse('get_total_revenue_by_api')
        request = self.factory.get(url)

        response = OrderAPIGetTotalRevenue.as_view()(request)

        self.assertIsInstance(response, JsonResponse)

        # Проверяем содержимое ответа
        expected_data = {'total_revenue': 0}  # Нет оплаченных заказов
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_data)


class OrderAPICreateTestCase(TestCase):
    def setUp(self):
        # Создаем клиент для выполнения запросов
        self.client = APIClient()
        # URL для создания заказа
        self.url = reverse('order_create')

    def test_create_order_valid_data(self):
        # Валидные данные для создания заказа
        valid_data = {
            'table_number': 34,
            'items': [
                {'position': 'Кола', 'price': 100},
                {'position': 'Картошка фри', 'price': 99.99},
            ]
        }

        # Выполняем POST-запрос
        response = self.client.post(self.url, data=valid_data, format='json')

        # Проверяем, что 1 заказ создан успешно
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        # Проверяем, что поля только для чтения заполнены автоматически
        order = Order.objects.first()
        self.assertIsNotNone(order.id)
        self.assertEqual(order.total_price, 199.99)
        self.assertEqual(order.status, 'в ожидании')

    def test_create_order_invalid_data(self):
        # Невалидные данные (отсутствует поле items)
        invalid_data = {
            'table_number': 34,
        }

        # Выполняем POST-запрос
        response = self.client.post(self.url, data=invalid_data, format='json')

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)  # Проверяем, что ошибка связана с полем items

    def test_create_order_invalid_items(self):
        # Невалидные данные (items не является списком)
        invalid_data = {
            'table_number': 5,
            'items': 'кола, картошка, 255, 144',  # Ожидается список
        }

        response = self.client.post(self.url, data=invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_create_order_invalid_items_structure(self):
        # Невалидные данные (items содержит некорректный элемент)
        invalid_data = {
            'table_number': 5,
            'items': [
                {'position': 'Кола', 'price': '144'},  # ключ price должен быть числом
            ]
        }

        response = self.client.post(self.url, data=invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_create_order_invalid_items_keys(self):
        # Невалидные данные (items содержит элемент с неправильными ключами)
        invalid_data = {
            'table_number': 5,
            'items': [
                {'name': 'Кола', 'cost': 250},  # Ожидаются ключи 'position' и 'price'
            ]
        }

        response = self.client.post(self.url, data=invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_create_order_empty_items(self):
        # Невалидные данные (items пустой)
        invalid_data = {
            'table_number': 5,
            'items': [],
        }

        response = self.client.post(self.url, data=invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_create_order_read_only_fields(self):
        # Данные с попыткой изменить read-only поля
        data_with_read_only = {
            'id': 10,  # Поле только для чтения
            'total_price': 240,  # Поле только для чтения
            'status': 'готово',  # Поле только для чтения
            'table_number': 11,
            'items': [
                {'position': 'Кола', 'price': 150},
            ]
        }

        response = self.client.post(self.url, data=data_with_read_only, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что read-only поля не изменились
        order = Order.objects.first()
        self.assertNotEqual(order.id, 10)
        self.assertNotEqual(order.total_price, 240)
        self.assertNotEqual(order.status, 'оплачено')

# -----------------------------------------------------------------------------
# Тесты для веб-интерфейса
# -----------------------------------------------------------------------------