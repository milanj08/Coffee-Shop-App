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
