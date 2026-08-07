"""Business logic for the cafe.

Nothing in this module imports from `rest_framework` or touches an HTTP
request. That is deliberate: the rules here can be exercised by a test, a
management command, or a scheduled job without a web server involved, and the
view's only job becomes translating exceptions into status codes.
"""

from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Accounting, InventoryManagement, Menu, Recipe, Sale


# --- Errors -----------------------------------------------------------------
# Plain Python exceptions, not DRF ones. The view maps these to status codes;
# the service stays unaware that HTTP exists.

class SaleError(Exception):
    """Base class for every reason a sale can be refused."""


class MenuItemNotFound(SaleError):
    def __init__(self, drink_name):
        self.drink_name = drink_name
        super().__init__(f"Menu item '{drink_name}' does not exist.")


class IngredientNotStocked(SaleError):
    """A recipe references an ingredient with no inventory row."""

    def __init__(self, ingredient_name):
        self.ingredient_name = ingredient_name
        super().__init__(
            f"Ingredient '{ingredient_name}' is required by a recipe but is not in inventory."
        )


class InsufficientStock(SaleError):
    def __init__(self, shortages):
        self.shortages = shortages
        detail = "; ".join(
            f"{s['ingredient']}: need {s['required']} {s['unit']}, have {s['available']}"
            for s in shortages
        )
        super().__init__(f"Insufficient stock. {detail}")


# --- Sales ------------------------------------------------------------------

@transaction.atomic
def record_sale(items, payment_method):
    """Record an order, deduct its ingredients, and update the balance.

    `items` is a list of {'drink_name': str, 'quantity': int}.

    Either the whole order succeeds or nothing is written - the decorator opens
    a transaction, and any exception raised below rolls the whole thing back.

    Returns {'total': Decimal, 'new_balance': Decimal}.
    """

    # 1. Resolve every drink up front, so an unknown name fails before we touch
    #    inventory rather than halfway through deducting.
    ordered = []
    for item in items:
        name = item['drink_name']
        try:
            menu_item = Menu.objects.get(name__iexact=name)
        except Menu.DoesNotExist:
            raise MenuItemNotFound(name)
        ordered.append((menu_item, item['quantity']))

    # 2. Ask the Recipe table what each drink needs. This is the entire point of
    #    the rewrite: no drink name appears anywhere in this function, so adding
    #    a new drink through the UI requires zero code changes.
    #
    #    One query for every recipe in the order, grouped in Python, rather than
    #    one query per drink.
    recipes_by_drink = defaultdict(list)
    recipe_rows = Recipe.objects.filter(
        recipe_name__in=[menu_item for menu_item, _ in ordered]
    ).select_related('ingredient_name')
    for row in recipe_rows:
        recipes_by_drink[row.recipe_name_id].append(row)

    # 3. Total the requirement per ingredient across the whole order. Two drinks
    #    that both use milk must be summed before we check stock, or each looks
    #    affordable on its own while the pair is not.
    required = defaultdict(Decimal)
    for menu_item, quantity in ordered:
        for row in recipes_by_drink[menu_item.pk]:
            required[row.ingredient_name_id] += row.ingredient_quantity * quantity

    # 4. Lock the inventory rows BEFORE reading the quantities we compare
    #    against. Without this, two simultaneous sales both read the same stock
    #    level, both compute a new one, and one deduction is silently lost.
    #
    #    Note: select_for_update() is a no-op on SQLite. The code is correct;
    #    the race is only genuinely closed on MySQL or PostgreSQL.
    stock = {
        row.pk: row
        for row in InventoryManagement.objects
        .select_for_update()
        .filter(pk__in=required.keys())
    }

    # 5. Check everything before writing anything. Report every shortage at once
    #    so the barista isn't told about them one order attempt at a time.
    shortages = []
    for ingredient_name, amount in required.items():
        row = stock.get(ingredient_name)
        if row is None:
            raise IngredientNotStocked(ingredient_name)
        if row.quantity < amount:
            shortages.append({
                'ingredient': row.name,
                'required': amount,
                'available': row.quantity,
                'unit': row.unit,
            })
    if shortages:
        raise InsufficientStock(shortages)

    # 6. Deduct. Stock is never floored at zero - step 5 guarantees it cannot go
    #    negative, and clamping would have hidden the overdraw instead.
    for ingredient_name, amount in required.items():
        row = stock[ingredient_name]
        row.quantity -= amount
        row.save(update_fields=['quantity'])

    # 7. Price the order from OUR data. The request body's `total`, if it sent
    #    one, is ignored - the client does not get to say how much money it paid.
    total = sum((menu_item.price * quantity for menu_item, quantity in ordered), Decimal('0.00'))

    # 8. One Sale row per line item, each recording the price actually charged.
    now = timezone.localtime()
    for menu_item, quantity in ordered:
        Sale.objects.create(
            time=now.time(),
            day=now.date(),
            quantity=quantity,
            drink=menu_item,
            payment_method=payment_method,
            price_charged=menu_item.price,
        )

    # 9. Append the new balance.
    #
    # Ordered by -id, not by -day/-time. Accounting is an append-only log, so
    # "latest" means "most recently inserted" - and id is the only field that
    # reliably says so. Ordering by the recorded timestamp trusts data that can
    # be wrong: a single row with a bad date sorts to the top forever, and
    # every later sale silently builds on a stale balance.
    #
    # That is not hypothetical. Before TIME_ZONE was corrected, an 8pm sale was
    # stamped 01:59 the following day. Every sale afterwards added to that row
    # instead of the real latest one, and the balance went down as trade came in.
    latest = Accounting.objects.order_by('-id').first()
    previous_balance = latest.account_balance if latest else Decimal('0.00')
    new_balance = previous_balance + total
    Accounting.objects.create(
        day=now.date(),
        time=now.time(),
        account_balance=new_balance,
    )

    return {'total': total, 'new_balance': new_balance}
