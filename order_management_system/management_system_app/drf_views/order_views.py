from rest_framework import generics, serializers
from ..models import Order
from ..serializers import OrderSerializer, OrderUpdateStatusSerializer, OrderUpdateItemsSerializer


class OrderAPICreate(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderAPIList(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        # Допустимые параметры запроса
        valid_params = ['status', 'table_number']

        # Получаем все параметры запроса
        request_params = self.request.query_params.keys()

        # Проверяем, есть ли некорректные параметры
        invalid_params = [param for param in request_params if param not in valid_params]
        if invalid_params:
            raise serializers.ValidationError(
                {
                    "error": f"Некорректные параметры запроса: {', '.join(invalid_params)}. Допустимые параметры: {', '.join(valid_params)}"}
            )

        # Получаем значения параметров
        status = self.request.query_params.get('status')
        table_number = self.request.query_params.get('table_number')

        # Допустимые значения для статуса
        valid_statuses = ['в ожидании', 'готово', 'оплачено']

        # Проверяем, не переданы ли оба параметра
        if status and table_number:
            raise serializers.ValidationError(
                {"error": "Можно искать только по одному параметру: status или table_number."}
            )

        # Проверяем, что status передан и не пустой
        if status is not None:  # Параметр присутствует в запросе
            if status == '':  # Параметр есть, но значение пустое
                raise serializers.ValidationError(
                    {"error": "Параметр 'status' не может быть пустым."}
                )
            if status not in valid_statuses:  # Некорректное значение
                raise serializers.ValidationError(
                    {
                        "error": f"Некорректное значение статуса: '{status}'. Допустимые значения: {', '.join(valid_statuses)}"}
                )
            # Фильтруем по status, если он корректен
            queryset = queryset.filter(status=status)

        # Фильтруем по table_number, если он передан и не пустой
        if table_number is not None:  # Параметр присутствует в запросе
            if table_number == '':  # Параметр есть, но значение пустое
                raise serializers.ValidationError(
                    {"error": "Параметр 'table_number' не может быть пустым."}
                )
            # Фильтруем по table_number
            queryset = queryset.filter(table_number=table_number)

        # Если заказы не найдены, выбрасываем ошибку
        if not queryset.exists():
            raise serializers.ValidationError({"error": "Заказы не найдены."})

        # если параметры не заданы, то возвращаются все заказы
        return queryset


class OrderAPIUpdateStatus(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateStatusSerializer

class OrderAPIUpdateItems(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateItemsSerializer

class OrderAPIDelete(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer