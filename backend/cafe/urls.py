from django.urls import path
from .views import (
    BaristaListCreateAPIView,
    ManagerListCreateAPIView,
    InventoryListCreateAPIView,
    MenuListCreateAPIView,
    PromotionListCreateAPIView,
    SaleListCreateAPIView,
    AccountingListCreateAPIView,
    RecipeListCreateAPIView,
    UpdateInventoryAPIView,
    CurrentBankAmountAPIView,
    RecordSaleAPIView,
    EmployeeDeleteAPIView,
    UpdateSalaryAPIView,
)

urlpatterns = [
    path('baristas/', BaristaListCreateAPIView.as_view(), name='baristas'),
    path('managers/', ManagerListCreateAPIView.as_view(), name='managers'),
    path('inventory/', InventoryListCreateAPIView.as_view(), name='inventory'),
    path('menu/', MenuListCreateAPIView.as_view(), name='menu'),
    path('promotions/', PromotionListCreateAPIView.as_view(), name='promotions'),
    path('sales/', SaleListCreateAPIView.as_view(), name='sales'),
    path('accounting/', AccountingListCreateAPIView.as_view(), name='accounting'),
    path('recipes/', RecipeListCreateAPIView.as_view(), name='recipes'),
    path('inventory/update/', UpdateInventoryAPIView.as_view(), name='update-inventory'),
    path('accounting/check/', CurrentBankAmountAPIView.as_view(), name='check-accounting'),
    path('accounting/purchase/', CurrentBankAmountAPIView.as_view(), name='check-accounting'),
    path('sales/record-sale', RecordSaleAPIView.as_view(), name='record-sale'),
    path('employees/delete/', EmployeeDeleteAPIView.as_view(), name='employee-delete'),
    path('employees/update-salary/', UpdateSalaryAPIView.as_view(), name='update-salary'),

]