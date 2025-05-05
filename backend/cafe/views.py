from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from datetime import date, datetime
from decimal import Decimal
from .models import (
    Barista, Manager, InventoryManagement, Menu,
    Promotion, Sale, Accounting, Recipe, Employee
)
from .serializers import (
    BaristaSerializer, ManagerSerializer, InventoryManagementSerializer,
    MenuSerializer, PromotionSerializer, SaleSerializer,
    AccountingSerializer, RecipeSerializer, EmployeeSerializer
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
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class PromotionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer


class SaleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class RecordSaleAPIView(APIView):
    def post(self, request):
        print("Full request data:", request.data)
        items = request.data.get('items', [])
        total_earnings = request.data.get('total')
        payment_method = request.data.get('payment_method')

        if not items:
            return Response({'error': 'Missing items'}, status=400)
        if total_earnings is None:
            return Response({'error': 'Missing total earnings'}, status=400)
        if not payment_method or not isinstance(payment_method, str):
            return Response({'error': 'Missing or invalid payment method'}, status=400)

        # Tracks how much of each ingredient we used in our order
        espressoUsed = 0.0
        milkUsed = 0.0
        chocUsed = 0.0

        # Iterate over items to ensure correct drink data
        for item in items:
            drink_name = item.get('drink_name')
            quantity = item.get('quantity', 0)

            # Look up our menu item 
            try:
                # Find which drink we have, and calculate how much of each ingredient we used
                drink = Menu.objects.get(name__iexact=drink_name)
                if drink_name == "Mocha":
                    espressoUsed += 2.0 * quantity
                    # Convert ml to L
                    milkUsed += (150.00 * quantity) / 1000
                    chocUsed += 80.00 * quantity
                elif drink_name == "Latte":
                    # Convert ml to L
                    milkUsed += (150.00 * quantity) / 1000
            except Menu.DoesNotExist:
                return Response({'error': f"Drink '{drink_name}' not found in the menu."})

            # Create the Sale
            Sale.objects.create(
                time=datetime.now().time(),
                day=date.today(),
                quantity=quantity,
                drink=drink,
                payment_method=payment_method)


        # Remove from our inventory how much we milk/espresso/chocolate syrup we used
        try:
            if espressoUsed > 0:
                espresso_item = InventoryManagement.objects.get(name="Espresso")

                if espresso_item.quantity < espressoUsed:
                    espresso_item.quantity = 0
                else:
                    espresso_item.quantity -= espressoUsed
                espresso_item.save()

            if milkUsed > 0:
                milk_item = InventoryManagement.objects.get(name="Milk")

                if milk_item.quantity < milkUsed:
                    milk_item.quantity = 0
                else:
                    milk_item.quantity -= milkUsed
                milk_item.save()

            if chocUsed > 0:
                choc_item = InventoryManagement.objects.get(name="Chocolate Syrup")

                if choc_item.quantity < chocUsed:
                    choc_item.quantity = 0
                else:
                    choc_item.quantity -= chocUsed
                choc_item.save()

        except InventoryManagement.DoesNotExist as e:
            return Response({'error': f"Ingredient '{e}' not found in inventory."})

        # Update the account balance
        total_earnings = Decimal(total_earnings)
        latest_entry = Accounting.objects.all().order_by('-day', '-time').first()
        current_balance = latest_entry.account_balance if latest_entry else Decimal("0.00")
        new_balance = current_balance + total_earnings

        # Make sure the balance doesn't go negative
        if new_balance < 0:
            new_balance = Decimal("0.00")

        # Create a new accounting entry
        Accounting.objects.create(
            account_balance=new_balance,
            day=date.today(),
            time=datetime.now().time()
        )

        return Response({
            'message': 'Sale recorded and account updated',
            'new_balance': str(new_balance)
        })
        

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
        latest_entry = Accounting.objects.all().order_by('-day', '-time').first()

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
        latest_entry = Accounting.objects.all().order_by('-day', '-time').first()
        if latest_entry:
            print("Current balance:", latest_entry.account_balance)
            return Response({
                'account_balance': latest_entry.account_balance
            })
        print("No accounting entries found. Returning 0.00")
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
