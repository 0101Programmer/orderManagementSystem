from rest_framework import generics
from ..models import Order
from ..serializers import OrderSerializer, OrderUpdateStatusSerializer


class OrderAPICreate(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderAPIList(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderAPIUpdateStatus(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateStatusSerializer
