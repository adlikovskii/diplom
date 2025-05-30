from django.db.models import Sum
from rest_framework import serializers

from .models import Order, OrderItem, Shop, Product, ProductInfo, Contact


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name')


class ListItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('order', 'product', 'quantity', 'shop')


class GetOrderSerializer(serializers.ModelSerializer):
    total_sum = serializers.SerializerMethodField()
    dt = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    orderitem_set = ListItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'dt', 'contact', 'orderitem_set', 'total_sum')

    def get_total_sum(self, obj):
        result = obj.orderitem_set.aggregate(sum_value=Sum('total_price'))
        return result.get('sum_value') or 0


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('model', 'quantity', 'price_rrc', 'shop', 'product')


class AddProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    product = AddProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('order', 'product', 'quantity', 'shop')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ('contact', 'order_items')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_context = self.context.get('user')
        if user_context:
            self.fields['contact'].queryset = Contact.objects.filter(user=user_context)


class ListOrderSerializer(serializers.ModelSerializer):
    dt = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'dt', 'total_sum')

    def get_total_sum(self, obj):
        data = obj.orderitem_set.aggregate(total=Sum('total_price'))
        return data.get('total') or 0


class ConfirmOrderSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=(('confirm', 'Подтвердить'),))

    class Meta:
        model = Order
        fields = ('id', 'status')