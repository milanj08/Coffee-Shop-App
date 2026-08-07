"""Tests for the sale service.

These call `record_sale` directly rather than going through HTTP. That is the
payoff of moving the logic out of the view: the rules can be exercised without
a server, a URL, or a serializer in the way.

Run with:  python manage.py test cafe
"""

from decimal import Decimal

from django.test import TestCase

from .models import Accounting, InventoryManagement, Menu, Recipe, Sale
from .serializers import RecipeSerializer
from .services import (
    InsufficientStock,
    MenuItemNotFound,
    record_sale,
)


class RecordSaleTests(TestCase):
    """Django gives each test a fresh database and rolls it back afterwards."""

    def setUp(self):
        self.milk = InventoryManagement.objects.create(
            name='Milk', unit='ml', quantity=Decimal('1000'), price=Decimal('3.50')
        )
        self.espresso = InventoryManagement.objects.create(
            name='Espresso', unit='g', quantity=Decimal('100'), price=Decimal('0.50')
        )
        self.mocha = Menu.objects.create(
            name='Mocha', size=350, type='coffee', price=Decimal('5.50'), hot_cold='hot'
        )
        Recipe.objects.create(
            recipe_name=self.mocha, ingredient_name=self.espresso,
            ingredient_quantity=Decimal('18'), ingredient_unit='g',
            position_number=1, execution_description='Pull a double shot.',
        )
        Recipe.objects.create(
            recipe_name=self.mocha, ingredient_name=self.milk,
            ingredient_quantity=Decimal('200'), ingredient_unit='ml',
            position_number=2, execution_description='Steam the milk.',
        )
        Accounting.objects.create(
            day='2026-01-01', time='09:00:00', account_balance=Decimal('100.00')
        )

    def test_deducts_ingredients_from_the_recipe_table(self):
        record_sale([{'drink_name': 'Mocha', 'quantity': 1}], 'cash')

        self.milk.refresh_from_db()
        self.espresso.refresh_from_db()
        self.assertEqual(self.milk.quantity, Decimal('800'))
        self.assertEqual(self.espresso.quantity, Decimal('82'))

    def test_multiplies_by_quantity_ordered(self):
        record_sale([{'drink_name': 'Mocha', 'quantity': 3}], 'cash')

        self.milk.refresh_from_db()
        self.assertEqual(self.milk.quantity, Decimal('400'))

    def test_price_comes_from_the_menu_not_the_request(self):
        result = record_sale([{'drink_name': 'Mocha', 'quantity': 2}], 'cash')

        # 2 x 5.50, regardless of anything a client might have claimed.
        self.assertEqual(result['total'], Decimal('11.00'))
        self.assertEqual(result['new_balance'], Decimal('111.00'))
        self.assertEqual(Sale.objects.get().price_charged, Decimal('5.50'))

    def test_a_new_drink_needs_no_code_change(self):
        """The whole point of the rewrite.

        A manager adds a drink and its recipe through the UI. Selling it
        deducts stock correctly, with nothing in Python mentioning its name.
        """
        cappuccino = Menu.objects.create(
            name='Cappuccino', size=250, type='coffee',
            price=Decimal('4.00'), hot_cold='hot',
        )
        Recipe.objects.create(
            recipe_name=cappuccino, ingredient_name=self.milk,
            ingredient_quantity=Decimal('120'), ingredient_unit='ml',
            position_number=1, execution_description='Steam and froth.',
        )

        record_sale([{'drink_name': 'Cappuccino', 'quantity': 1}], 'cash')

        self.milk.refresh_from_db()
        self.assertEqual(self.milk.quantity, Decimal('880'))

    def test_insufficient_stock_writes_nothing(self):
        self.milk.quantity = Decimal('50')
        self.milk.save()

        with self.assertRaises(InsufficientStock):
            record_sale([{'drink_name': 'Mocha', 'quantity': 1}], 'cash')

        # The transaction rolled back: no sale, no deduction, no balance change.
        self.milk.refresh_from_db()
        self.espresso.refresh_from_db()
        self.assertEqual(self.milk.quantity, Decimal('50'))
        self.assertEqual(self.espresso.quantity, Decimal('100'))
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(Accounting.objects.count(), 1)

    def test_balance_builds_on_the_last_row_inserted_not_the_latest_date(self):
        """Regression: a mis-dated Accounting row used to poison every sale.

        A row stamped in the future sorted first under order_by('-day','-time'),
        so subsequent sales added to a stale balance and the total went down as
        trade came in.
        """
        Accounting.objects.create(
            day='2099-01-01', time='09:00:00', account_balance=Decimal('1.00')
        )

        result = record_sale([{'drink_name': 'Mocha', 'quantity': 1}], 'cash')

        # Builds on the 1.00 row - it was inserted last - not on the 100.00 one.
        self.assertEqual(result['new_balance'], Decimal('6.50'))

    def test_requirements_are_totalled_across_the_order(self):
        """Two drinks are affordable alone but not together."""
        latte = Menu.objects.create(
            name='Latte', size=350, type='coffee', price=Decimal('4.50'), hot_cold='hot'
        )
        Recipe.objects.create(
            recipe_name=latte, ingredient_name=self.milk,
            ingredient_quantity=Decimal('300'), ingredient_unit='ml',
            position_number=1, execution_description='Steam the milk.',
        )
        self.milk.quantity = Decimal('400')
        self.milk.save()

        with self.assertRaises(InsufficientStock):
            record_sale(
                [
                    {'drink_name': 'Mocha', 'quantity': 1},   # 200 ml
                    {'drink_name': 'Latte', 'quantity': 1},   # 300 ml
                ],
                'cash',
            )

    def test_unknown_drink_is_rejected(self):
        with self.assertRaises(MenuItemNotFound):
            record_sale([{'drink_name': 'Flat White', 'quantity': 1}], 'cash')

        self.assertEqual(Sale.objects.count(), 0)

    def test_multi_item_order_writes_one_sale_row_each(self):
        """Used to be impossible: unique_together on (time, day) rejected the
        second row, because both are written in the same instant."""
        latte = Menu.objects.create(
            name='Latte', size=350, type='coffee', price=Decimal('4.50'), hot_cold='hot'
        )
        Recipe.objects.create(
            recipe_name=latte, ingredient_name=self.milk,
            ingredient_quantity=Decimal('300'), ingredient_unit='ml',
            position_number=1, execution_description='Steam the milk.',
        )

        record_sale(
            [
                {'drink_name': 'Mocha', 'quantity': 1},
                {'drink_name': 'Latte', 'quantity': 1},
            ],
            'cash',
        )

        self.assertEqual(Sale.objects.count(), 2)
        self.milk.refresh_from_db()
        self.assertEqual(self.milk.quantity, Decimal('500'))


class RecipeUnitValidationTests(TestCase):
    """A recipe must be written in the unit its ingredient is stocked in.

    Without this, milk stocked in ml and a recipe written in liters would
    deduct 1000x too little and nothing would complain - which is the bug the
    original code papered over with a hardcoded /1000.
    """

    def setUp(self):
        self.milk = InventoryManagement.objects.create(
            name='Milk', unit='ml', quantity=Decimal('1000'), price=Decimal('3.50')
        )
        self.latte = Menu.objects.create(
            name='Latte', size=350, type='coffee', price=Decimal('4.50'), hot_cold='hot'
        )

    def payload(self, unit):
        return {
            'recipe_name': 'Latte',
            'ingredient_name': 'Milk',
            'ingredient_quantity': '300.00',
            'ingredient_unit': unit,
            'position_number': 1,
            'execution_description': 'Steam the milk.',
        }

    def test_rejects_a_unit_the_ingredient_is_not_stocked_in(self):
        serializer = RecipeSerializer(data=self.payload('liters'))

        self.assertFalse(serializer.is_valid())
        self.assertIn('ingredient_unit', serializer.errors)

    def test_accepts_a_matching_unit(self):
        serializer = RecipeSerializer(data=self.payload('ml'))

        # Passing serializer.errors as the message means a failure tells you
        # what was wrong instead of just "False is not True".
        self.assertTrue(serializer.is_valid(), serializer.errors)
