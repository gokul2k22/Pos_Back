

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Category, Product, Customer, Inventory, Sale, SalesDetail
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CustomerSerializer,
    InventorySerializer,
    SaleSerializer,
    SalesDetailSerializer
)

# Generic class to handle GET, POST, PUT, DELETE
class BaseAPIView(APIView):
    model = None
    serializer_class = None

    def get(self, request):
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        response = Response(serializer.data)
        response['Content-Type'] = 'application/json; charset=utf-8'  # ✅ Add this line
        return response

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, pk=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Views for each model using BaseAPIView
class CategoryAPIView(BaseAPIView):
    model = Category
    serializer_class = CategorySerializer



class CustomerAPIView(BaseAPIView):
    model = Customer
    serializer_class = CustomerSerializer

class InventoryAPIView(BaseAPIView):
    model = Inventory
    serializer_class = InventorySerializer

class SaleAPIView(BaseAPIView):
    model = Sale
    serializer_class = SaleSerializer

class SalesDetailAPIView(BaseAPIView):
    model = SalesDetail
    serializer_class = SalesDetailSerializer


class ProductAPIView(BaseAPIView):
    model = Product
    serializer_class = ProductSerializer
    def get(self, request):
        category_id = request.query_params.get('category', None)
        if category_id:
            products = Product.objects.filter(category_id=category_id)
        else:
            products = Product.objects.all()

        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)
    
    

class SaleCreateAPIView(APIView):
    GUEST_CUSTOMER_ID = 1  # Default guest fallback

    def get(self, request, *args, **kwargs):
        sales = Sale.objects.all().order_by('-sale_date')
        serializer = SaleSerializer(sales, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        print("📦 Incoming request data:", data)

        products_data = data.get("products")
        total_amount = data.get("total_amount")
        total_quantity = data.get("total_quantity")
        customer_data = data.get("customer")

        if not products_data or total_amount is None:
            return Response({"error": "Missing products or total amount."}, status=400)

        try:
            with transaction.atomic():
                # ----------------------
                # ✅ Handle Customer
                # ----------------------
                if customer_data and customer_data.get("phone"):
                    phone = customer_data["phone"].strip()
                    name = customer_data.get("name", "").strip()

                    customer, created = Customer.objects.get_or_create(
                        phone=phone,
                        defaults={"first_name": name}
                    )

                    # Update name if customer exists and name is newly provided
                    if not created and name and customer.first_name != name:
                        customer.first_name = name
                        customer.save()
                else:
                    # Fallback to Guest (id=1)
                    customer = Customer.objects.get(id=self.GUEST_CUSTOMER_ID)

                # ----------------------
                # ✅ Create Sale
                # ----------------------
                sale = Sale.objects.create(
                    customer=customer,
                    total_amount=total_amount
                )

                # ----------------------
                # ✅ Add Products to Sale
                # ----------------------
                for item in products_data:
                    product_name = item["name"]
                    quantity = item["quantity"]
                    price = item["price"]

                    print(f"📦 Processing product: {product_name}, Quantity: {quantity}, Price: {price}")

                    product = Product.objects.filter(name=product_name).first()
                    if not product:
                        raise Exception(f"Product '{product_name}' not found.")

                    SalesDetail.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                    # Update inventory if available
                    try:
                        inventory = Inventory.objects.get(product=product)
                        if inventory.quantity < quantity:
                            raise Exception(f"Insufficient inventory for '{product.name}'.")
                        inventory.quantity -= quantity
                        inventory.save()
                    except Inventory.DoesNotExist:
                        print(f"⚠️ Inventory not found for {product.name}, skipping.")

                # ----------------------
                # ✅ Final Response
                # ----------------------
                return Response({
                    "message": "Sale recorded successfully.",
                    "sale_id": sale.id,
                    "total_amount": str(sale.total_amount),
                    "total_quantity": total_quantity
                }, status=201)

        except Exception as e:
            print(f"❌ Error during sale creation: {str(e)}")
            return Response({"error": str(e)}, status=500)

