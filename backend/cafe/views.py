from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from datetime import date, datetime
from decimal import Decimal
from .models import (
    Barista, Manager, InventoryManagement, Menu,
    Promotion, Sale, Accounting, Recipe, Employee
)
from .serializers import (
    BaristaSerializer, ManagerSerializer, InventoryManagementSerializer,
    MenuSerializer, PromotionSerializer, SaleSerializer,
    AccountingSerializer, RecipeSerializer, EmployeeSerializer,
    RecordSaleSerializer
)
from .services import (
    record_sale, MenuItemNotFound, IngredientNotStocked, InsufficientStock
)


class BaristaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BaristaSerializer

    def get_queryset(self):
        queryset = Barista.objects.all()

        # Access query parameters and filter based on them
        first_name = self.request.query_params.get('first_name', None)
        if first_name:
            queryset = queryset.filter(ssn__first_name__icontains=first_name)

        return queryset


class ManagerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ManagerSerializer

    def get_queryset(self):
        queryset = Manager.objects.all()

        # Access query parameters and filter based on them
        first_name = self.request.query_params.get('first_name', None)
        if first_name:
            queryset = queryset.filter(ssn__first_name__icontains=first_name)

        return queryset


class InventoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = InventoryManagement.objects.all()
    serializer_class = InventoryManagementSerializer

# Handles updating quantity of an item in our inventory
class UpdateInventoryAPIView(APIView):
    def patch(self, request):
        # Checking if our data was sent properly
        print("Received data:", request.data)

        try:
            # Get list of items from request
            order_items = request.data.get("order", [])

            # For each item in orders, add how much product we ordered to our exisitng quantity
            for item in order_items:
                inventory_item = InventoryManagement.objects.get(name=item['name'])
                inventory_item.quantity += item['quantity']
                inventory_item.save()

            return Response({"message": "Inventory updated successfully"})
        except Exception as e:
            return Response({"error": str(e)})


class MenuListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MenuSerializer

    def get_queryset(self):
        """Supports ?name=<drink>.

        Previously this was a bare `queryset = Menu.objects.all()`, so the
        query parameter was silently ignored and every menu item came back.
        The frontend took data[0] from that, which meant every drink was
        priced as whichever row happened to be first.

        iexact, not icontains: this is a lookup for one specific drink, not a
        search. "Latte" must not match "Iced Latte".
        """
        queryset = Menu.objects.all()

        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__iexact=name)

        return queryset


class PromotionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer


class SaleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class RecordSaleAPIView(APIView):
    """POST /api/sales/record-sale

    Three lines of responsibility: validate the payload, call the service,
    translate its exceptions into status codes. No business rules live here.
    """

    def post(self, request):
        serializer = RecordSaleSerializer(data=request.data)
        # raise_exception=True lets DRF's handler produce the 400 and the
        # field-keyed error body, instead of us assembling one by hand.
        serializer.is_valid(raise_exception=True)

        try:
            result = record_sale(
                items=serializer.validated_data['items'],
                payment_method=serializer.validated_data['payment_method'],
            )
        except MenuItemNotFound as error:
            return Response({'error': str(error)}, status=status.HTTP_404_NOT_FOUND)
        except InsufficientStock as error:
            # 409 Conflict: the request is well-formed but conflicts with the
            # current state of the shop. Nothing was written.
            return Response(
                {'error': str(error), 'shortages': error.shortages},
                status=status.HTTP_409_CONFLICT,
            )
        except IngredientNotStocked as error:
            # A recipe references an ingredient with no inventory row. That is a
            # data problem on our side, not a bad request.
            return Response(
                {'error': str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                'message': 'Sale recorded and account updated',
                'total': str(result['total']),
                'new_balance': str(result['new_balance']),
            },
            status=status.HTTP_200_OK,
        )



class AccountingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Accounting.objects.all()
    serializer_class = AccountingSerializer

class CurrentBankAmountAPIView(APIView):
    # Used when a purchase is made in inventory management
    def post(self, request):
        # Gets how much our total purchase came out to
        total_purchase = request.data.get('total_purchase')

        if total_purchase is None:
             return Response({'error': 'Missing total_cost'})

        # Turns it into a decimal before subtracting
        total_purchase = Decimal(total_purchase)

        # Gets our most recent accounting form based on the most recent day and time
        # -id, not -day/-time: see the note in services.record_sale. Ordering an
        # append-only balance log by its own recorded timestamp means one bad
        # date poisons every subsequent read.
        latest_entry = Accounting.objects.all().order_by('-id').first()

        # If we find an entry, subtract our total purchase from it
        # If we cant find one or it becomes a negative value, set it to 0.00
        if latest_entry:
            new_balance = latest_entry.account_balance - total_purchase
            if new_balance < 0:
                new_balance = Decimal("0.00")
        else:
            new_balance = Decimal("0.00")

        # Save a new accounting entry
        new_entry = Accounting.objects.create(
            account_balance=new_balance,
            day=date.today(),
            time=datetime.now().time()
        )

        return Response({'message': 'Account updated', 'new_balance': str(new_entry.account_balance)})
   
    # Used to check the balance in our account
    def get(self, request):
        
         # Gets our most recent accounting form based on the most recent day and time
        # -id, not -day/-time: see the note in services.record_sale. Ordering an
        # append-only balance log by its own recorded timestamp means one bad
        # date poisons every subsequent read.
        latest_entry = Accounting.objects.all().order_by('-id').first()
        if latest_entry:
            # str(), so this endpoint returns the same type as every other
            # one. DRF renders a bare Decimal as a JSON number, which drops the
            # trailing zero - 50014.50 arrives as 50014.5. One endpoint giving
            # a number while the rest give strings is a trap for the caller.
            return Response({'account_balance': str(latest_entry.account_balance)})
        return Response({'account_balance': "0.00"})


class RecipeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()

        # Access query parameters and filter based on them
        recipe_name = self.request.query_params.get('recipe_name', None)
        if recipe_name:
            queryset = queryset.filter(recipe_name__name__icontains=recipe_name)

        return queryset

class EmployeeDeleteAPIView(APIView):
    """
    Delete an employee (Barista or Manager) using their SSN via query param.
    Example: DELETE /api/employees/delete/?ssn=123-45-6789
    """

    def delete(self, request):
        ssn = request.query_params.get('ssn', None)
        if not ssn:
            return Response({'error': 'SSN parameter is required'})
        try:
            # Try deleting Barista
            employee = Barista.objects.filter(ssn=ssn).first()
            if employee:
                employee.delete()
                return Response({'message': 'Barista deleted successfully'})

            # Try deleting Manager
            employee = Manager.objects.filter(ssn=ssn).first()
            if employee:
                employee.delete()
                return Response({'message': 'Manager deleted successfully'})

            return Response({'error': 'Employee not found'})

        except Exception as e:
            return Response({'error': str(e)})
        
class UpdateSalaryAPIView(APIView):
    """
    Update the salary of an Employee (Barista or Manager) using their SSN via query param.
    Example: PUT /api/employees/update-salary/?ssn=123-45-6789
    """

    def put(self, request):
        ssn = request.query_params.get('ssn')
        new_salary = request.data.get('salary')

        if not ssn or new_salary is None:
            return Response({'error': 'SSN and salary are required'}, status=400)

        try:
            new_salary = Decimal(new_salary)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid salary value'}, status=400)

        # Find the employee by SSN
        employee = Employee.objects.filter(ssn=ssn).first()
        if not employee:
            return Response({'error': 'Employee not found'}, status=404)

        # Use the serializer to validate and save the updated salary
        employee.salary = new_salary
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)  # `partial=True` allows updating only certain fields

        if serializer.is_valid():
            serializer.save()  # Save the employee with the updated salary
            return Response({'message': 'Employee salary updated successfully'}, status=200)

        return Response(serializer.errors, status=400)
