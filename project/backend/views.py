from django.core.validators import URLValidator
from django.db import IntegrityError
from django.http import JsonResponse
from requests import get
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load as yaml_load, Loader

from users.confirm import send_confirmed_order
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem
from .permissions import IsOwnerOrder, IsOwnerOrderItem
from .serializers import (ProductInfoSerializer, OrderSerializer, ListItemsSerializer, OrderItemSerializer,
                          ListOrderSerializer, ConfirmOrderSerializer, GetOrderSerializer)


class UploadProductsView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Error': 'Authentication required.'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Error': 'Only shops are permitted to upload products.'}, status=403)

        url = request.data.get('url')
        if not url:
            return JsonResponse({'Error': 'URL parameter is missing.'}, status=400)

        validator = URLValidator()
        try:
            validator(url)
        except ValidationError as e:
            return JsonResponse({'Error': str(e)}, status=400)

        try:
            content = get(url).content
            data = yaml_load(content, Loader=Loader)
        except Exception as e:
            return JsonResponse({'Error': f'Failed to load YAML from URL: {e}'}, status=400)

        try:
            shop, created = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)

            for cat in data.get('categories', []):
                cat_obj, _ = Category.objects.get_or_create(
                    external_id=cat['id'],
                    name=cat['name']
                )
                cat_obj.shops.add(shop)

            for item in data.get('goods', []):
                prod_obj, _ = Product.objects.get_or_create(
                    name=item['name'],
                    category=Category.objects.get(external_id=item['category'])
                )

                try:
                    prod_info_obj, _ = ProductInfo.objects.get_or_create(
                        product=prod_obj,
                        model=item['model'],
                        external_id=item['id'],
                        shop=shop,
                        quantity=item['quantity'],
                        price=item['price'],
                        price_rrc=item['price_rrc']
                    )
                except IntegrityError:
                    # Duplicate product info, skip this item
                    continue

                for param_name, param_value in item['parameters'].items():
                    param_obj, _ = Parameter.objects.get_or_create(name=param_name)
                    ProductParameter.objects.get_or_create(
                        product_info=prod_info_obj,
                        parameter=param_obj,
                        value=param_value
                    )

            return JsonResponse({'Success': 'Products uploaded successfully.'}, status=200)

        except KeyError as e:
            return JsonResponse({'Error': f'Missing key in data: {e}'}, status=400)


class ListProductView(ListAPIView):
    queryset = ProductInfo.objects.select_related('product').prefetch_related('shop', 'product__category')
    serializer_class = ProductInfoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['model', 'product__name', 'shop__name', 'product__category__name']
    ordering_fields = ['model', 'product__name', 'shop__name', 'product__category__name', 'price_rrc', 'quantity']


class ListItemsOrder(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListItemsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['model', 'product__name', 'shop__name', 'product__category__name']
    ordering_fields = ['model', 'product__name', 'shop__name', 'product__category__name', 'price_rrc']

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user, order__status='new').select_related('product')


class AddOrderItemView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        serializer.validated_data['user'] = user

        order, created = Order.objects.get_or_create(
            user=user,
            contact=serializer.validated_data['contact'],
            status='new'
        )

        info = {}
        for item in serializer.validated_data.get('orderitem_set', []):
            product_id = item['product']['id']
            shop_id = item['shop']

            product = Product.objects.get(id=product_id, product_info__shop_id=shop_id)
            product_info = product.product_info.filter(shop_id=shop_id).first()
            available_qty = product_info.quantity if product_info else 0

            product_item = OrderItem.objects.filter(order=order, product=product).first()

            requested_qty = item['quantity']
            if product_item:
                total_requested = product_item.quantity + requested_qty
                if total_requested > available_qty:
                    return Response(
                        {'Error': f'Insufficient stock for {product.name}. Available: {available_qty - product_item.quantity}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                product_item.quantity = total_requested
                product_item.save()
                info[product.name] = 'updated quantity in order'
            else:
                if requested_qty > available_qty:
                    return Response(
                        {'Error': f'Insufficient stock for {product.name}. Available: {available_qty}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                OrderItem.objects.create(order=order, product=product, shop=shop_id, quantity=requested_qty)
                info[product.name] = 'added to order'

        return Response({"Success": "Item(s) added successfully", "details": info}, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        return {'user': self.request.user}


class DeleteOrderItemView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrderItem]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self.perform_destroy(obj)
        return Response({"Success": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class ListOrderView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class DetailOrderView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrder]
    queryset = Order.objects.select_related('user', 'contact').prefetch_related('orderitem_set__product')
    serializer_class = GetOrderSerializer


class ConfirmOrderView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrder]
    serializer_class = ConfirmOrderSerializer
    queryset = Order.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)

        if order.status in ['confirmed', 'assembled', 'sent', 'delivered', 'canceled']:
            return Response({"Order status": order.status}, status=status.HTTP_403_FORBIDDEN)

        order.status = 'confirmed'

        order_summary = {
            'order_id': order.id,
            'user_id': order.user.id,
            'user': order.user.username,
            'price_order': 0,
            'products': {}
        }

        for item in order.orderitem_set.all():
            product = item.product
            order_summary['products'][product.name] = {
                'quantity': item.quantity,
                'total_price': item.total_price,
                'id': item.id
            }
            order_summary['price_order'] += item.total_price

            prod_info = product.product_info.filter(shop=item.shop).first()
            if prod_info:
                prod_info.quantity -= item.quantity
                prod_info.save()

        send_confirmed_order(order_summary, [request.user.email])
        order.save()

        return Response({"Success": "Order confirmed successfully"}, status=status.HTTP_200_OK)