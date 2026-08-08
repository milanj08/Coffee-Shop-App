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
    RecordSaleSerializer, RestockSerializer, EmployeeLookupSerializer
)
from .services import (
    record_sale, restock, delete_employee,
    MenuItemNotFound, IngredientNotStocked, InsufficientStock, EmployeeNotFound
)
from .permissions import IsManager, IsManagerOrReadOnly, IsStaff

# Every view below declares permission_classes explicitly.
#
# settings.py now defaults to IsAuthenticated, so forgetting one fails closed
# rather than open - the opposite of the previous AllowAny default, where a new
# endpoint was public unless you remembered otherwise. Stating it on each view
# anyway means you can read a class and know who may call it without going to
# settings.
#
#   IsStaff             any signed-in employee
#   IsManagerOrReadOnly employees may read, managers may write
#   IsManager           managers only


class BaristaListCreateAPIView(generics.ListCreateAPIView):
    # Employee records: names, emails, SSNs, shifts. Managers only.
    permission_classes = [IsManager]
    serializer_class = BaristaSerializer

    def get_queryset(self):
        queryset = Barista.objects.all()

        # Access query parameters and filter based on them
        first_name = self.request.query_params.get('first_name', None)
        if first_name:
            queryset = queryset.filter(ssn__first_name__icontains=first_name)

        return queryset


class ManagerListCreateAPIView(generics.ListCreateAPIView):
    # POST here creates a manager, so this is the privilege-escalation route.
    permission_classes = [IsManager]
    serializer_class = ManagerSerializer

    def get_queryset(self):
        queryset = Manager.objects.all()

        # Access query parameters and filter based on them
        first_name = self.request.query_params.get('first_name', None)
        if first_name:
            queryset = queryset.filter(ssn__first_name__icontains=first_name)

        return queryset


class InventoryListCreateAPIView(generics.ListCreateAPIView):
    # A barista needs to see stock levels; only a manager adds new items.
    permission_classes = [IsManagerOrReadOnly]
    queryset = InventoryManagement.objects.all()
    serializer_class = InventoryManagementSerializer

# Handles updating quantity of an item in our inventory
class UpdateInventoryAPIView(APIView):
    """PATCH /api/inventory/update/ - add purchased stock.

    Was: read request.data straight, loop, save each row, and wrap the lot in
    `except Exception` returning a 200. That meant an unvalidated payload, a
    KeyError on a missing field, partial writes on failure, and - because
    Response defaults to status 200 - a failed restock that looked identical to
    a successful one.
    """

    # Restocking moves money and stock. Managers only.
    permission_classes = [IsManager]

    def patch(self, request):
        serializer = RestockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            restock(serializer.validated_data['order'])
        except IngredientNotStocked as error:
            # Naming an item that isn't stocked is the caller's mistake, and
            # 404 says which kind: the resource doesn't exist.
            return Response({'error': str(error)}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Inventory updated successfully'})


class MenuListCreateAPIView(generics.ListCreateAPIView):
    # Baristas read the menu constantly; changing prices is a manager decision.
    permission_classes = [IsManagerOrReadOnly]
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
    permission_classes = [IsManagerOrReadOnly]
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer


class SaleListCreateAPIView(generics.ListCreateAPIView):
    # Sales history is a reporting view, not something a barista needs.
    permission_classes = [IsManager]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class RecordSaleAPIView(APIView):
    """POST /api/sales/record-sale

    Three lines of responsibility: validate the payload, call the service,
    translate its exceptions into status codes. No business rules live here.
    """

    # The one write a barista is meant to perform.
    permission_classes = [IsStaff]

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
    # The books. Managers only.
    permission_classes = [IsManager]
    queryset = Accounting.objects.all()
    serializer_class = AccountingSerializer

class CurrentBankAmountAPIView(APIView):
    permission_classes = [IsManager]

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
    # A barista must read recipe steps to make the drink; editing a recipe
    # changes what gets deducted from stock, so that is a manager action.
    permission_classes = [IsManagerOrReadOnly]
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()

        # Access query parameters and filter based on them
        recipe_name = self.request.query_params.get('recipe_name', None)
        if recipe_name:
            queryset = queryset.filter(recipe_name__name__icontains=recipe_name)

        return queryset

class EmployeeDeleteAPIView(APIView):
    """DELETE /api/employees/delete/?ssn=123456789

    Was: delete the Barista row, or failing that the Manager row, and return
    200 for everything including "not found". Two problems.

    Every response was 200 - a missing employee and a successful delete were
    indistinguishable without reading the body.

    And it left an orphan. on_delete=CASCADE runs Employee -> Barista, not the
    reverse, so removing the Barista row left the Employee behind. Once logins
    existed it left the User and its token too, which meant a "deleted"
    employee could still authenticate. Deleting the Employee is what actually
    removes the person; the cascade handles their role row.
    """

    permission_classes = [IsManager]

    def delete(self, request):
        serializer = EmployeeLookupSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            delete_employee(serializer.validated_data['ssn'])
        except EmployeeNotFound as error:
            return Response({'error': str(error)}, status=status.HTTP_404_NOT_FOUND)

        # 204: succeeded, and there is nothing to return. The old 200 with a
        # message body was describing an outcome the status code already gives.
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class UpdateSalaryAPIView(APIView):
    """PATCH /api/employees/update-salary/?ssn=123456789

    PATCH, not PUT. PUT means "replace the whole resource" - a PUT that only
    sends one field and relies on partial=True is a PATCH wearing the wrong
    verb, and it means a client sending a full object would silently do a
    partial update instead.

    Also removed a dead line: `employee.salary = new_salary` was assigned and
    then immediately overwritten by the serializer on the next statement.
    """

    permission_classes = [IsManager]

    def patch(self, request):
        lookup = EmployeeLookupSerializer(data=request.query_params)
        lookup.is_valid(raise_exception=True)

        employee = Employee.objects.filter(pk=lookup.validated_data['ssn']).first()
        if not employee:
            return Response(
                {'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND
            )

        # The serializer validates and saves. validate_salary() rejects
        # anything <= 0, so no manual Decimal parsing is needed here.
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Employee salary updated successfully'}, status=200)

        return Response(serializer.errors, status=400)
