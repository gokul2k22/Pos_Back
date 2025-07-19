from rest_framework import serializers
from .models import Category, Product, Customer, Inventory, Sale, SalesDetail

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'



class SalesDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SalesDetail
        fields = ['product', 'product_name', 'quantity', 'price']
class SaleSerializer(serializers.ModelSerializer):
    products = serializers.ListField(write_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(  # write-only
        source='customer',
        queryset=Customer.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    customer = CustomerSerializer(read_only=True)  # read-only with full data
    sale_details = SalesDetailSerializer(source='details', many=True, read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'total_amount', 'customer', 'customer_id', 'sale_date', 'products', 'sale_details']

    def create(self, validated_data):
        products_data = validated_data.pop('products', [])
        sale = Sale.objects.create(**validated_data)

        for item in products_data:
            product_name = item.get('name')
            quantity = item.get('quantity')
            price = item.get('price')

            try:
                product = Product.objects.filter(name=product_name).first()
                if not product:
                    raise serializers.ValidationError(f"Product '{product_name}' not found.")
            except Exception as e:
                raise serializers.ValidationError(f"Error processing product '{product_name}': {str(e)}")

            SalesDetail.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price,
            )

        return sale

    # def create(self, validated_data):
    #     details_data = validated_data.pop('details')
    #     sale = Sale.objects.create(**validated_data)
    #     for detail_data in details_data:
    #         SalesDetail.objects.create(sale=sale, **detail_data)
    #     return sale


class SalesDetailNestedSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetail
        fields = ['product', 'product_name', 'quantity', 'price', 'total_price']

    def get_total_price(self, obj):
        return float(obj.quantity) * float(obj.price)