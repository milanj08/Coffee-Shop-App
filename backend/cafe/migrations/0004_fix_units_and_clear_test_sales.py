"""Clean up the data that the 0003 schema change assumes.

Three jobs:
  1. Remove 15 Sale rows from a May 2025 demo session. Their matching
     Accounting entries were deleted at some point (the surviving row has
     id=26, so 25 were created and removed), which left the database asserting
     $92.50 of revenue that the balance does not reflect. Backfilling
     price_charged would have made that contradiction permanent.
  2. Stock every ingredient in the unit its recipes are written in, so no
     conversion layer is needed. Milk was held in liters while every recipe row
     was in ml; espresso was held in ambiguous "oz" when beans are bought and
     dosed by weight.
  3. Replace invented recipe quantities that were internally inconsistent - a
     latte calling for 0.25 ml of milk, and a mocha needing 380 ml of milk in a
     350 ml cup.
"""

from decimal import Decimal

from django.db import migrations


def fix_data(apps, schema_editor):
    # Historical model versions, not the ones in models.py. This is why data
    # migrations keep working after the models change again later.
    Inventory = apps.get_model('cafe', 'InventoryManagement')
    Recipe = apps.get_model('cafe', 'Recipe')
    Sale = apps.get_model('cafe', 'Sale')

    Sale.objects.all().delete()

    Inventory.objects.filter(name='Milk').update(
        unit='ml', quantity=Decimal('19000'))
    Inventory.objects.filter(name='Espresso').update(
        unit='g', quantity=Decimal('2000'))
    Inventory.objects.filter(name='Chocolate Syrup').update(
        unit='ml')

    # Latte: 300 ml of milk.
    Recipe.objects.filter(
        recipe_name_id='Latte', ingredient_name_id='Milk'
    ).update(ingredient_quantity=Decimal('300'), ingredient_unit='ml')

    # Mocha: 18 g of beans, 200 ml of milk, 30 ml of syrup.
    Recipe.objects.filter(
        recipe_name_id='Mocha', ingredient_name_id='Espresso'
    ).update(ingredient_quantity=Decimal('18'), ingredient_unit='g')

    Recipe.objects.filter(
        recipe_name_id='Mocha', ingredient_name_id='Milk', position_number=2
    ).update(ingredient_quantity=Decimal('200'), ingredient_unit='ml')

    # The second milk step (position 4) put total milk over the cup size.
    Recipe.objects.filter(
        recipe_name_id='Mocha', ingredient_name_id='Milk', position_number=4
    ).delete()

    Recipe.objects.filter(
        recipe_name_id='Mocha', ingredient_name_id='Chocolate Syrup'
    ).update(ingredient_quantity=Decimal('30'), ingredient_unit='ml')


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0003_alter_sale_unique_together_sale_price_charged_and_more'),
    ]

    operations = [
        # No reverse: deleted sales cannot be recovered, so rolling this
        # migration back is a no-op rather than a lie.
        migrations.RunPython(fix_data, migrations.RunPython.noop),
    ]
