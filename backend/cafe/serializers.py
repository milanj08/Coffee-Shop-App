import random
from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from .models import (Employee, Barista, Manager, InventoryManagement, Menu,
                     Promotion, Sale, Accounting, Recipe)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['ssn', 'first_name', 'last_name', 'email', 'salary']
    
    # Custom validation for salary field
    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than 0.")
        return value


class BaristaSerializer(serializers.ModelSerializer):
    ssn = EmployeeSerializer()

    class Meta:
        model = Barista
        fields = '__all__'

    def create(self, validated_data):
        employee_data = validated_data.pop('ssn')
        employee = Employee.objects.create(**employee_data)
        barista = Barista.objects.create(ssn=employee, **validated_data)
        return barista


class ManagerSerializer(serializers.ModelSerializer):
    ssn = EmployeeSerializer()

    class Meta:
        model = Manager
        fields = '__all__'

    def create(self, validated_data):
        employee_data = validated_data.pop('ssn')
        employee = Employee.objects.create(**employee_data)
        manager = Manager.objects.create(ssn=employee, **validated_data)
        return manager


class InventoryManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryManagement
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class PromotionSerializer(serializers.ModelSerializer):
    menu = serializers.SlugRelatedField(queryset=Menu.objects.all(), slug_field='name')

    class Meta:
        model = Promotion
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    drink = serializers.SlugRelatedField(queryset=Menu.objects.all(), slug_field='name')

    class Meta:
        model = Sale
        fields = '__all__'


class AccountingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounting
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    recipe_name = serializers.SlugRelatedField(queryset=Menu.objects.all(), slug_field='name')
    ingredient_name = serializers.SlugRelatedField(queryset=InventoryManagement.objects.all(), slug_field='name')

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        """A recipe must be written in the unit its ingredient is stocked in.

        Object-level rather than field-level, because it compares two fields.
        This is what makes unit mismatches impossible instead of converted:
        milk stocked in ml and a recipe written in liters would otherwise
        deduct 1000x too little and nothing would complain.
        """
        ingredient = data.get('ingredient_name')
        unit = data.get('ingredient_unit')
        if ingredient is not None and unit is not None and unit != ingredient.unit:
            raise serializers.ValidationError({
                'ingredient_unit': (
                    f"Must be '{ingredient.unit}', the unit "
                    f"'{ingredient.name}' is stocked in."
                )
            })
        return data


class AccountSerializer(serializers.Serializer):
    """The shape returned by login and by /api/auth/me/.

    Read-only. `role` is derived from the Barista/Manager tables on every
    request - it is never sent by the client and never stored on the User.
    """

    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)


def _allocate_placeholder_ssn():
    """Invent an unused employee key for a self-registered account.

    This function exists only because SSN is the primary key of Employee. A
    surrogate integer key would make it unnecessary, which is one more argument
    for the change noted in the README. A manager sets the real value later.
    """
    for _ in range(20):
        candidate = Decimal(random.randint(100000000, 999999999))
        if not Employee.objects.filter(pk=candidate).exists():
            return candidate
    raise serializers.ValidationError(
        'Could not allocate an employee record. Try again.'
    )


class RegisterSerializer(serializers.Serializer):
    """Self-service signup, which always produces a barista.

    Deliberately has no `role` field. The original bug was that the client
    decided the role; letting a registration payload ask for 'manager' would
    reintroduce it with extra steps. Manager accounts are created by a manager,
    or seeded in the demo fixture.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('That username is already taken.')
        return value

    def validate_password(self, value):
        """Run Django's configured password validators.

        AUTH_PASSWORD_VALIDATORS has been sitting in settings.py unused since
        the project was generated, because the old login never touched Django's
        auth system. This is what turns it on.
        """
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(list(error.messages))
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Three inserts, all or nothing.

        Without the transaction a failure partway leaves a User with no
        Employee, or an Employee with no Barista row - which Employee.role
        reads as "no role", so the account would authenticate and then be
        denied everywhere with no obvious cause.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
        )

        employee = Employee.objects.create(
            ssn=_allocate_placeholder_ssn(),
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            salary=Decimal('0.00'),
            user=user,
        )

        # The Barista row IS the role. No separate column to keep in sync.
        Barista.objects.create(
            ssn=employee,
            day=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

        return employee


class RestockItemSerializer(serializers.Serializer):
    """One line of a restocking purchase."""

    name = serializers.CharField(max_length=255)
    # min_value matters here. The old endpoint added whatever number arrived, so
    # a negative quantity REMOVED stock through a restocking endpoint - and
    # nothing checked, because the payload was read straight off request.data.
    quantity = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal('0.01')
    )


class RestockSerializer(serializers.Serializer):
    """The request body of PATCH /api/inventory/update/."""

    order = RestockItemSerializer(many=True, allow_empty=False)


class EmployeeLookupSerializer(serializers.Serializer):
    """Validates the ?ssn= query parameter.

    Rejecting a malformed SSN with a 400 before it reaches the database is
    cheaper than catching whatever the ORM raises when a DecimalField primary
    key is handed the string "abc".
    """

    ssn = serializers.RegexField(r'^\d{9}$', error_messages={
        'invalid': 'SSN must be exactly 9 digits.',
    })


class SaleItemSerializer(serializers.Serializer):
    """One line of an order."""

    drink_name = serializers.CharField(max_length=30)
    quantity = serializers.IntegerField(min_value=1)


class RecordSaleSerializer(serializers.Serializer):
    """The request body of POST /api/sales/record-sale.

    Note what is absent: `total`. The frontend still sends one and it is
    ignored. Price is computed server-side from Menu.price, because a client
    that can name its own total can name zero.
    """

    items = SaleItemSerializer(many=True, allow_empty=False)
    payment_method = serializers.ChoiceField(choices=Sale.PaymentMethod.choices)
