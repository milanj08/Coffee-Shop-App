from django.db import models
from django.core.exceptions import ValidationError

# Create your models here
# --- Employees ---
class Employee(models.Model):
    ssn = models.DecimalField(max_digits=9, decimal_places=0, primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

# --- Baristas ---
class Barista(models.Model):
    ssn = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

# --- Managers ---
class Manager(models.Model):
    ssn = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    percentage_ownership = models.DecimalField(max_digits=5, decimal_places=2)

# --- Inventory Management ---
class InventoryManagement(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    unit = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# --- Menu ---
class Menu(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    size = models.DecimalField(max_digits=5, decimal_places=2)
    type = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    hot_cold = models.CharField(max_length=4)

    def clean(self):
        if self.hot_cold not in ['hot', 'cold']:
            raise ValidationError('hot_cold must be "hot" or "cold"')
        if self.type not in ['tea', 'coffee', 'softdrink']:
            raise ValidationError('type must be tea, coffee, or softdrink')

# --- Promotions ---
class Promotion(models.Model):
    day = models.DateField()
    time = models.TimeField()
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    promotion_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('day', 'time', 'menu'),)

# --- Sales ---
class Sale(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        CREDIT_CARD = 'credit card', 'Credit Card'
        APP = 'app', 'App'

    time = models.TimeField()
    day = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    drink = models.ForeignKey(Menu, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)

    class Meta:
        unique_together = (('time', 'day'),)

# --- Accounting ---
class Accounting(models.Model):
    day = models.DateField()
    time = models.TimeField()
    account_balance = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        unique_together = (('day', 'time'),)

# --- Recipes ---
class Recipe(models.Model):
    recipe_name = models.ForeignKey(Menu, on_delete=models.CASCADE)
    ingredient_name = models.ForeignKey(InventoryManagement, on_delete=models.CASCADE)
    ingredient_quantity = models.DecimalField(max_digits=20, decimal_places=2)
    ingredient_unit = models.CharField(max_length=5)
    position_number = models.PositiveSmallIntegerField()
    execution_description = models.TextField()

    class Meta:
        unique_together = (('recipe_name', 'position_number'),)
