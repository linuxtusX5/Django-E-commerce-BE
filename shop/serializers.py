from rest_framework import serializers
from .models import Category, Product, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_name', 'name', 'slug', 'description', 'price', 'stock', 'image', 'available', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'product', 'product_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'email', 'first_name', 'last_name', 'address', 'city', 'postal_code', 'country', 'status', 'created_at', 'total_price', 'items']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(write_only=True)

    class Meta:
        model = Order
        fields = ['email', 'first_name', 'last_name', 'address', 'city', 'postal_code', 'country', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        total = 0

        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            total += product.price * item['quantity']

        order = Order.objects.create(**validated_data, total_price=total)

        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item['quantity']
            )
            product.stock -= item['quantity']
            product.save()

        return order
