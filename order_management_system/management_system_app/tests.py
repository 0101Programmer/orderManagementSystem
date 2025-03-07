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

class OrderAPIListTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('order_list')

        Order.objects.create(table_number=1, items=
        [{"position": "Картофель фри", "price": 100}, {"position": "Шашлык", "price": 200}],
                             status='оплачено')
        Order.objects.create(table_number=2, items=
        [{"position": "Картофель фри", "price": 300}, {"position": "Шашлык", "price": 400}],
                             status='в ожидании')
        Order.objects.create(table_number=3, items=
        [{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
                             status='готово')
        Order.objects.create(table_number=4, items=
        [{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
                             status='в ожидании')

    def test_get_all_orders(self):
        # Выполняем GET-запрос без параметров
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # Проверяем, что возвращены все заказы

    def test_filter_by_status(self):
        # Выполняем GET-запрос с параметром status
        response = self.client.get(self.url, {'status': 'в ожидании'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Проверяем, что возвращено 2 заказа
        # и у обоих запрошенный статус
        self.assertEqual(response.data[0]['status'], 'в ожидании')
        self.assertEqual(response.data[1]['status'], 'в ожидании')

    def test_filter_by_table_number(self):
        # Выполняем GET-запрос с параметром table_number
        response = self.client.get(self.url, {'table_number': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Проверяем, что возвращен только один заказ
        self.assertEqual(response.data[0]['table_number'], 2)

    def test_invalid_status(self):
        # Выполняем GET-запрос с некорректным статусом
        response = self.client.get(self.url, {'status': 'готов'})

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status param error', response.data)  # Проверяем, что ошибка связана с некорректным статусом

    def test_invalid_table_number(self):
        # Выполняем GET-запрос с пустым table_number
        response = self.client.get(self.url, {'table_number': ''})

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('table_number param error', response.data)  # Проверяем, что ошибка связана с table_number

    def test_invalid_params(self):
        # Выполняем GET-запрос с некорректными параметрами
        response = self.client.get(self.url, {'table_id': 11})

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('params error', response.data)  # Проверяем, что ошибка связана с некорректными параметрами

    def test_no_orders_found(self):
        # Выполняем GET-запрос с параметром, по которому заказы не будут найдены
        response = self.client.get(self.url, {'table_number': 999})

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('no orders error', response.data)  # Проверяем, что ошибка связана с отсутствием заказов

class OrderAPIUpdateStatusTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаем тестовый заказ
        self.order = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='в ожидании'
        )
        # URL для обновления статуса заказа
        self.url = reverse('order_update_status', args=[self.order.id])

    def test_update_status_valid_data(self):
        # Валидные данные для обновления статуса
        valid_data = {
            'status': 'готово'
        }

        # Выполняем PATCH-запрос
        response = self.client.patch(self.url, data=valid_data, format='json')

        # Проверяем, что статус заказа обновлен успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.order.status, 'готово')

    def test_update_status_invalid_data(self):
        # Невалидные данные (недопустимый статус)
        invalid_data = {
            'status': 'доставка'
        }

        response = self.client.patch(self.url, data=invalid_data, format='json')

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)  # Проверяем, что ошибка связана с полем status

    def test_update_status_empty_data(self):
        # Невалидные данные (пустой статус)
        invalid_data = {
            'status': ''
        }

        response = self.client.patch(self.url, data=invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)  # Проверяем, что ошибка связана с полем status

    def test_update_status_read_only_fields(self):
        # Попытка изменить read-only поля
        invalid_data = {
            'table_number': 2,  # Поле только для чтения
            'status': 'готово'
        }

        response = self.client.patch(self.url, data=invalid_data, format='json')

        # Проверяем, что запрос успешен, но read-only поля не изменились
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.order.table_number, 4)  # Поле table_number не изменилось
        self.assertEqual(self.order.status, 'готово')  # Поле status изменилось

class OrderAPIUpdateItemsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.order = Order.objects.create(
            table_number=6,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}]
        )
        # URL для обновления содержимого заказа
        self.url = reverse('order_update_items', args=[self.order.id])

    def test_update_items_valid_data(self):
        # Валидные данные для обновления содержимого
        valid_data = {
            'items': [{"position": "Жаркое", "price": 499.99}, {"position": "Сок", "price": 200.50}]
        }

        # Выполняем PATCH-запрос
        response = self.client.patch(self.url, data=valid_data, format='json')

        # Проверяем, что статус заказа обновлен успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.order.items, [{"position": "Жаркое", "price": 499.99},
                                            {"position": "Сок", "price": 200.50}])

    def test_update_items_invalid_data(self):
        # Невалидные данные
        invalid_data = {
            'items': [{"pos": "Жаркое", "price": 499.99}, {"position": "Сок", "price": 200.50}]
        }

        response = self.client.patch(self.url, data=invalid_data, format='json')

        # Проверяем, что запрос отклонен с ошибкой 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)  # Проверяем, что ошибка связана с полем items

    def test_update_items_empty_data(self):
        # Невалидные данные (пустой список)
        invalid_data = {
            'items': []
        }

        response = self.client.patch(self.url, data=invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_update_items_read_only_fields(self):
        # Попытка изменить read-only поля
        invalid_data = {
            'table_number': 2,  # Поле только для чтения
            'items': [{"position": "Шаурма", "price": 199.99},
                      {"position": "Минералка", "price": 100}]
        }

        response = self.client.patch(self.url, data=invalid_data, format='json')

        # Проверяем, что запрос успешен, но read-only поля не изменились
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.order.table_number, 6)  # Поле table_number не изменилось
        self.assertEqual(self.order.items,
                         [{"position": "Шаурма", "price": 199.99},
                      {"position": "Минералка", "price": 100}])  # Поле items изменилось

class OrderAPIDeleteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.order = Order.objects.create(
            table_number=10,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
        )
        # URL для удаления заказа
        self.url = reverse('order_delete', args=[self.order.id])

    def test_delete_order(self):
        # Выполняем DELETE-запрос
        response = self.client.delete(self.url)

        # Проверяем, что заказ удален успешно
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())  # Проверяем, что заказ удален из базы данных

    def test_delete_nonexistent_order(self):
        # Удаляем заказ
        self.order.delete()

        # Выполняем DELETE-запрос для несуществующего заказа
        response = self.client.delete(self.url)

        # Проверяем, что запрос отклонен с ошибкой 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# -----------------------------------------------------------------------------
# Тесты для веб-интерфейса
# -----------------------------------------------------------------------------