from django.conf import settings
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

    # Login identity, kept separate from employment data. Django's User owns
    # the username and the hashed password; Employee owns SSN, salary, and who
    # this person is to the business. They answer different questions.
    #
    # SET_NULL rather than CASCADE: deleting a login should not erase the
    # employment record. null=True because employees can exist before they have
    # an account - the five in the demo fixture predate this feature.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee',
    )

    @property
    def role(self):
        """Derived from the specialization tables, not stored anywhere.

        The schema already encodes this: a Barista row means barista, a Manager
        row means manager. Adding a `role` column would create a second source
        of truth that can disagree with these tables.

        `hasattr` on a reverse one-to-one returns False when the row is absent,
        because the descriptor raises RelatedObjectDoesNotExist.

        Manager is checked first, so an employee holding both rows is treated
        as a manager. Nothing currently prevents an employee having both, or
        neither - a known gap, noted in the README.
        """
        if hasattr(self, 'manager'):
            return 'manager'
        if hasattr(self, 'barista'):
            return 'barista'
        return None

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
    # Decimal, not integer: a recipe can call for 0.5 of a unit, and an integer
    # column silently rounds it away. SQLite tolerated this; MySQL will not.
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# --- Menu ---
class Menu(models.Model):
    """These rules used to live in a clean() method, which never ran.

    Nothing calls full_clean() on its own - not save(), not objects.create(),
    not DRF's serializer.save(). Only Django ModelForms do, and this project has
    none. So `hot_cold: "lukewarm"` saved happily through the API for a year.

    choices moves the constraint onto the field, where DRF turns it into a
    ChoiceField and rejects bad values with a 400 before anything is written.
    Sale.PaymentMethod already did this correctly; Menu just never got the same
    treatment.
    """

    class DrinkType(models.TextChoices):
        TEA = 'tea', 'Tea'
        COFFEE = 'coffee', 'Coffee'
        SOFT_DRINK = 'softdrink', 'Soft Drink'

    class Temperature(models.TextChoices):
        HOT = 'hot', 'Hot'
        COLD = 'cold', 'Cold'

    name = models.CharField(max_length=30, primary_key=True)
    size = models.DecimalField(max_digits=5, decimal_places=2)
    type = models.CharField(max_length=20, choices=DrinkType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    hot_cold = models.CharField(max_length=4, choices=Temperature.choices)

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
    # You cannot sell 2.5 lattes.
    quantity = models.PositiveIntegerField()
    drink = models.ForeignKey(Menu, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    # Snapshot of Menu.price at the moment of sale. Without this, a manager
    # editing the menu silently reprices every historical sale of that drink.
    price_charged = models.DecimalField(max_digits=10, decimal_places=2)

    # NOTE: previously `unique_together = (('time', 'day'),)`, which allowed one
    # sale per second shop-wide. A two-item order writes two rows with the same
    # timestamp, so this constraint made the endpoint impossible to fix.

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
    # Must equal the unit its ingredient is stocked in - enforced in
    # RecipeSerializer.validate(). max_length was 5, so "liters" never fit.
    ingredient_unit = models.CharField(max_length=50)
    position_number = models.PositiveSmallIntegerField()
    execution_description = models.TextField()

    class Meta:
        unique_together = (('recipe_name', 'position_number'),)
