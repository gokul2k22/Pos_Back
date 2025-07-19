from django.urls import path
# from .views import ProductCategoryEditView, ProductCategoryViewSet,ProductViewSet
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    CategoryAPIView, ProductAPIView, CustomerAPIView,
    InventoryAPIView, SaleAPIView, SalesDetailAPIView,SaleCreateAPIView
)

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryAPIView.as_view(), name='category-detail'),

    path('products/', ProductAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductAPIView.as_view(), name='product-detail'),

    path('customers/', CustomerAPIView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerAPIView.as_view(), name='customer-detail'),

    path('inventories/', InventoryAPIView.as_view(), name='inventory-list'),
    path('inventories/<int:pk>/', InventoryAPIView.as_view(), name='inventory-detail'),

    path('sales/', SaleCreateAPIView.as_view(), name='sale-list'),
    path('sales/<int:pk>/', SaleAPIView.as_view(), name='sale-detail'),

    path('sales-details/', SalesDetailAPIView.as_view(), name='sales-detail-list'),
    path('sales-details/<int:pk>/', SalesDetailAPIView.as_view(), name='sales-detail-detail'),
    
    path('sales/create/', SaleCreateAPIView.as_view(), name='sale-create'),

]

