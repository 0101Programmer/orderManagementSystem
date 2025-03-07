from django.test import TestCase, RequestFactory, Client
from django.http import JsonResponse
from rest_framework import status
from rest_framework.test import APIClient

from .forms import AddOrderForm, DeleteOrderForm, GetOrderForm, UpdateOrderItemsForm, UpdateOrderStatusForm
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
class AddOrderTestCase(TestCase):
    def setUp(self):
        # Создаем клиент для выполнения запросов
        self.client = Client()
        # URL для добавления заказа
        self.url = reverse('add_order')

    def test_get_add_order_form(self):
        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что форма отображается
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/add_order.html')
        self.assertIsInstance(response.context['form'], AddOrderForm)
        self.assertContains(response, 'Добавление заказа')

    def test_post_valid_data(self):
        # Валидные данные для добавления заказа
        valid_data = {
            'table_number': 7,
            'items': '[{"position": "Картофель фри", "price": 500}]'
        }

        # Выполняем POST-запрос
        response = self.client.post(self.url, data=valid_data)

        # Проверяем, что заказ создан успешно
        self.assertEqual(response.status_code, 302)  # Проверяем перенаправление
        self.assertEqual(Order.objects.count(), 1)  # Проверяем, что заказ создан

        # Проверяем, что произошло перенаправление
        self.assertRedirects(response, reverse('add_order'))

    def test_post_invalid_data(self):
        # Невалидные данные (отсутствует поле items)
        invalid_data = {
            'table_number': 9,
        }

        response = self.client.post(self.url, data=invalid_data)

        # Проверяем, что форма возвращается с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/add_order.html')
        self.assertFormError(response.context['form'], 'items', 'Обязательное поле.')

class DeleteOrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем тестовые заказы
        self.order1 = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
        )
        self.order2 = Order.objects.create(
            table_number=14,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
        )
        # URL для удаления заказа
        self.url = reverse('delete_order')

    def test_get_delete_order_form(self):
        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что форма отображается
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/delete_order.html')
        self.assertIsInstance(response.context['form'], DeleteOrderForm)
        self.assertContains(response, 'Удаление заказа')

    def test_post_valid_data(self):
        # Валидные данные для удаления заказа
        valid_data = {
            'order_id': self.order1.id
        }

        # Выполняем POST-запрос
        response = self.client.post(self.url, data=valid_data)

        # Проверяем, что заказ удален успешно
        self.assertEqual(response.status_code, 302)  # Проверяем перенаправление
        self.assertFalse(Order.objects.filter(id=self.order1.id).exists())  # Проверяем, что заказ удален

        # Проверяем, что произошло перенаправление
        self.assertRedirects(response, reverse('delete_order'))

class GetAllOrdersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.order1 = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
        )
        self.order2 = Order.objects.create(
            table_number=14,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
        )

        # URL для получения всех заказов
        self.url = reverse('get_all_orders')

    def test_get_all_orders(self):
        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_all_orders.html')

        # Проверяем, что в контексте передаются все заказы
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 2)  # Проверяем, что переданы 2 заказа

        # Проверяем, что ID заказов отображаются на странице
        self.assertContains(response, 4)
        self.assertContains(response, 14)

class GetOrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.order1 = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='в ожидании'
        )
        self.order2 = Order.objects.create(
            table_number=14,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='готово'
        )
        self.order3 = Order.objects.create(
            table_number=18,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='готово'
        )
        self.order4 = Order.objects.create(
            table_number=18,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='оплачено'
        )

        # URL для поиска заказов по номеру стола или статусу
        self.url = reverse('get_order')

    def test_get_order_form(self):
        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что форма отображается
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_order.html')
        self.assertIsInstance(response.context['form'], GetOrderForm)
        self.assertContains(response, 'Поиск заказа')

    def test_search_by_table_number(self):
        # Валидные данные для поиска по номеру стола
        search_data = {
            'table_number': 18
        }

        # Выполняем GET-запрос с параметрами поиска
        response = self.client.get(self.url, data=search_data)

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_order.html')

        # Проверяем, что в контексте передаются найденные заказы
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 2)  # Проверяем, что найдено 2 заказа
        self.assertEqual(response.context['orders'][0].table_number,
                         18)  # Проверяем, что каждый заказ соответствует номеру стола
        self.assertEqual(response.context['orders'][1].table_number,
                         18)

    def test_search_by_status(self):
        # Валидные данные для поиска по статусу
        search_data = {
            'status': 'готово'
        }

        response = self.client.get(self.url, data=search_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_order.html')

        # Проверяем, что в контексте передаются найденные заказы
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 2)  # Проверяем, что найдено 2 заказа
        self.assertEqual(response.context['orders'][0].status, 'готово')  # Проверяем, что каждый заказ соответствует статусу
        self.assertEqual(response.context['orders'][1].status, 'готово')

    def test_search_with_both_fields(self):
        # Невалидные данные (заполнены оба поля)
        invalid_data = {
            'table_number': 18,
            'status': 'в ожидании'
        }

        # Выполняем GET-запрос с параметрами поиска
        response = self.client.get(self.url, data=invalid_data)

        # Проверяем, что форма возвращается с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_order.html')
        self.assertFormError(response.context['form'], None,
                             'Заполните только одно поле: либо номер стола, либо статус заказа.')

    def test_search_with_no_fields(self):
        # Невалидные данные (не заполнено ни одно поле)
        invalid_data = {
            'table_number': '',
            'status': ''
        }

        response = self.client.get(self.url, data=invalid_data)

        # Проверяем, что форма возвращается с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_order.html')
        self.assertFormError(response.context['form'], None,
                             'Заполните хотя бы одно поле: номер стола или статус заказа.')

class GetTotalRevenueTestCase(TestCase):
    def setUp(self):
        # Создаем клиент для выполнения запросов
        self.client = Client()
        # URL для расчета выручки
        self.url = reverse('get_total_revenue')

    def test_get_total_revenue_with_paid_orders(self):
        # Создаем оплаченные заказы
        Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='оплачено'
        )
        Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='оплачено'
        )

        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_total_revenue.html')

        # Проверяем, что в контексте передается правильная выручка
        self.assertIn('total_revenue', response.context)
        self.assertEqual(response.context['total_revenue'], 2200)

        # Проверяем, что выручка отображается на странице
        self.assertContains(response, '2200')

    def test_get_total_revenue_with_no_paid_orders(self):
        # Создаем заказы с другими статусами
        Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='готово'
        )
        Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='в ожидании'
        )

        response = self.client.get(self.url)

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_total_revenue.html')

        # Проверяем, что в контексте передается выручка 0
        self.assertIn('total_revenue', response.context)
        self.assertEqual(response.context['total_revenue'], 0)  # Нет оплаченных заказов

        # Проверяем, что выручка 0 отображается на странице
        self.assertContains(response, '0')

    def test_get_total_revenue_with_empty_database(self):
        # База данных пуста (нет заказов)

        response = self.client.get(self.url)

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/get_total_revenue.html')

        # Проверяем, что в контексте передается выручка 0
        self.assertIn('total_revenue', response.context)
        self.assertEqual(response.context['total_revenue'], 0)  # Нет заказов

        # Проверяем, что выручка 0 отображается на странице
        self.assertContains(response, '0')

class UpdateOrderItemsTestCase(TestCase):
    def setUp(self):
        # Создаем клиент для выполнения запросов
        self.client = Client()
        # Создаем тестовый заказ
        self.order = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='оплачено'
        )
        # URL для обновления заказа
        self.url = reverse('update_order_items', args=[self.order.id])

    def test_get_update_order_items_form(self):
        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что форма отображается
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/update_order_items.html')
        self.assertIsInstance(response.context['form'], UpdateOrderItemsForm)
        self.assertContains(response, 'Изменение содержимого заказа')

    def test_post_valid_data(self):
        # Валидные данные для обновления заказа
        valid_data = {
            'items': '[{"position": "Кола зеро", "price": 50}, {"position": "Шаурма", "price": 199.99}]'
        }

        # Выполняем POST-запрос
        response = self.client.post(self.url, data=valid_data)

        # Проверяем, что заказ обновлен успешно
        self.assertEqual(response.status_code, 302)  # Проверяем перенаправление
        self.order.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.order.items, [{"position": "Кола зеро", "price": 50},
                                            {"position": "Шаурма", "price": 199.99}])  # Проверяем, что items обновлены

        # Проверяем, что произошло перенаправление
        self.assertRedirects(response, reverse('update_order_items', args=[self.order.id]))

    def test_post_invalid_data(self):
        # Невалидные данные (items не является JSON)
        invalid_data = {
            'items': 'Картофель, овощи, 150, 99'
        }

        response = self.client.post(self.url, data=invalid_data)

        # Проверяем, что форма возвращается с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/update_order_items.html')
        self.assertFormError(response.context['form'], 'items', 'Введите корректный JSON.')

    def test_post_empty_data(self):
        # Невалидные данные (пустое поле items)
        invalid_data = {
            'items': ''
        }

        response = self.client.post(self.url, data=invalid_data)

        # Проверяем, что форма возвращается с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/update_order_items.html')
        self.assertFormError(response.context['form'], 'items', 'Обязательное поле.')

class UpdateOrderStatusTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.order1 = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='оплачено'
        )
        self.order2 = Order.objects.create(
            table_number=4,
            items=[{"position": "Картофель фри", "price": 500}, {"position": "Шашлык", "price": 600}],
            status='в ожидании'
        )
        # URL для обновления статуса заказа
        self.url = reverse('update_order_status')

    def test_get_update_order_status_form(self):
        # Выполняем GET-запрос
        response = self.client.get(self.url)

        # Проверяем, что форма отображается
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders_crud_web_inter/update_order_status.html')
        self.assertIsInstance(response.context['form'], UpdateOrderStatusForm)
        self.assertContains(response, 'Изменение статуса заказа')

    def test_post_valid_data(self):
        # Валидные данные для обновления статуса заказа
        valid_data = {
            'order_id': self.order1.id,
            'status': 'готово'
        }

        # Выполняем POST-запрос
        response = self.client.post(self.url, data=valid_data)

        # Проверяем, что статус заказа обновлен успешно
        self.assertEqual(response.status_code, 302)  # Проверяем перенаправление
        self.order1.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.order1.status, 'готово')  # Проверяем, что статус обновлен

        # Проверяем, что произошло перенаправление
        self.assertRedirects(response, reverse('update_order_status'))