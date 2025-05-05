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
    RecordSaleAPIView
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
]

# Example of a POST request to add a manager
#  curl -X POST http://localhost:8000/api/managers/ \
# -H "Content-Type: application/json" \
# -d '{
#     "ssn": {
#         "ssn": "121212121",
#         "first_name": "Michael",
#         "last_name": "James",
#         "email": "mjames@example.com",
#         "salary": 9500.00
#     },
#     "percentage_ownership": 25.50
# }'                                                                                                                                                               <....
# {"ssn":{"ssn":"121212121","first_name":"Michael","last_name":"James","email":"mjames@example.com","salary":"9500.00"},"percentage_ownership":"25.50"}%

# Example of a POST request to add a barista
# curl -X POST http://localhost:8000/api/baristas/ \
# -H "Content-Type: application/json" \
# -d '{
#     "ssn": {
#         "ssn": "232323234",
#         "first_name": "Miles",
#         "last_name": "Jones",
#         "email": "mjones@example.com",
#         "salary": 6000.00
#     },
#     "day": "2025-05-01",
#     "start_time": "08:00:00",
#     "end_time": "16:00:00"
# }'
# {"ssn":{"ssn":"232323234","first_name":"Miles","last_name":"Jones","email":"mjones@example.com","salary":"6000.00"},"day":"2025-05-01","start_time":"08:00:00","end_time":"16:00:00"}

# Example of GET request to get a Barista or all baristas
# (venv) (base) jonathanhung@Jonathans-MacBook-Pro cs480project % curl "http://localhost:8000/api/baristas/?first_name=Bob"
#
# [{"ssn":{"ssn":"987654321","first_name":"Bob","last_name":"Johnson","email":"bob.johnson@example.com","salary":"60000.00"},"day":"2025-05-02","start_time":"09:00:00","end_time":"17:00:00"}]%
# (venv) (base) jonathanhung@Jonathans-MacBook-Pro cs480project % curl "http://localhost:8000/api/baristas/"
#
# [{"ssn":{"ssn":"123456789","first_name":"Alice","last_name":"Smith","email":"alice@example.com","salary":"50000.00"},"day":"2025-05-01","start_time":"08:00:00","end_time":"16:00:00"},{"ssn":{"ssn":"987654321","first_name":"Bob","last_name":"Johnson","email":"bob.johnson@example.com","salary":"60000.00"},"day":"2025-05-02","start_time":"09:00:00","end_time":"17:00:00"},{"ssn":{"ssn":"232323234","first_name":"Miles","last_name":"Jones","email":"mjones@example.com","salary":"6000.00"},"day":"2025-05-01","start_time":"08:00:00","end_time":"16:00:00"}]%


# Example of a POST request to add an inventory item
# curl -X POST http://localhost:8000/api/inventory/ \
#   -H "Content-Type: application/json" \
#   -d '{
#     "name": "Milk",
#     "unit": "liters",
#     "quantity": 10,
#     "price": "3.50"
# }'
#
# {"name":"Milk","unit":"liters","quantity":10,"price":"3.50"}%

# Example to POST and GET a recipe step from the recipes table
# curl -X POST http://localhost:8000/api/recipes/ \
#   -H "Content-Type: application/json" \
#   -d '{
#     "recipe_name": "Latte",
#     "ingredient_name": "Milk",
#     "ingredient_quantity": "0.25",
#     "ingredient_unit": "ml",
#     "position_number": 1,
#     "execution_description": "Steam the milk and pour into espresso"
# }'
#
# {"id":2,"recipe_name":"Latte","ingredient_name":"Milk","ingredient_quantity":"0.25","ingredient_unit":"ml","position_number":1,"execution_description":"Steam the milk and pour into espresso"}%
#
# curl "http://localhost:8000/api/recipes/?recipe_name=Latte"
# [{"id":2,"recipe_name":"Latte","ingredient_name":"Milk","ingredient_quantity":"0.25","ingredient_unit":"ml","position_number":1,"execution_description":"Steam the milk and pour into espresso"}]%