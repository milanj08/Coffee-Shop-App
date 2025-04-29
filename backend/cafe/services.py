from .models import Employee, Barista, Manager, InventoryManagement, Menu, Promotion, Sale, Accounting, Recipe
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

# Functions to add entries to tables
def add_barista(ssn, first_name, last_name, email, salary, day, start_time, end_time):
    try:
        emp = Employee(
            ssn=ssn,
            first_name=first_name,
            last_name=last_name,
            email=email,
            salary=salary
        )
        emp.full_clean()
        emp.save()

        barista = Barista(
            ssn=emp,
            day=day,
            start_time=start_time,
            end_time=end_time
        )
        barista.full_clean()
        barista.save()

        return emp
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

def add_manager(ssn, first_name, last_name, email, salary, percentage):
    try:
        emp = Employee(
            ssn=ssn,
            first_name=first_name,
            last_name=last_name,
            email=email,
            salary=salary
        )
        emp.full_clean()
        emp.save()

        manager = Manager(
            ssn=emp,
            percentage_ownership=percentage
        )
        manager.full_clean()
        manager.save()

        return emp
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

def add_inventory_item(name, unit, quantity, price):
    try:
        item = InventoryManagement(
            name=name,
            unit=unit,
            quantity=quantity,
            price=price
        )
        item.full_clean()
        item.save()
        return item
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

def add_menu_item(name, size, drink_type, price, hot_cold):
    try:
        menu_item = Menu(
            name=name,
            size=size,
            type=drink_type,
            price=price,
            hot_cold=hot_cold
        )
        menu_item.full_clean()
        menu_item.save()
        return menu_item
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

def add_sale(sale_time, sale_day, quantity, drink_name, payment_method):
    try:
        drink = Menu.objects.get(name=drink_name)

        sale = Sale(
            time=sale_time,
            day=sale_day,
            quantity=quantity,
            drink=drink,
            payment_method=payment_method
        )
        sale.full_clean()
        sale.save()

        print("Sale successfully added.")
        return sale

    except Menu.DoesNotExist:
        print(f"Menu item '{drink_name}' does not exist.")
    except ValidationError as e:
        print(f"Validation error: {e}")
    return None

def add_account_entry(day, time, balance):
    try:
        account_entry = Accounting(
            day=day,
            time=time,
            account_balance=balance
        )
        account_entry.full_clean()
        account_entry.save()
        return account_entry
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

def add_recipe_item(name, i_name, i_quantity, i_unit, pos_number, description):
    try:
        recipe = Recipe(
            recipe_name=name,
            ingredient_name=i_name,
            ingredient_quantity=i_quantity,
            ingredient_unit=i_unit,
            position_number=pos_number,
            execution_description=description
        )
        recipe.full_clean()
        recipe.save()
        return recipe
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

def add_promotion(day, time, menu_name, promotion_price):
    try:
        menu_item = Menu.objects.get(name=menu_name)
        promo = Promotion(
            day=day,
            time=time,
            menu=menu_item,
            promotion_price=promotion_price
        )
        promo.full_clean()  # Validate fields and unique constraint
        promo.save()        # Save to DB
        return promo
    except Menu.DoesNotExist:
        print(f"Menu item '{menu_name}' does not exist.")
    except ValidationError as e:
        print(f"Validation failed: {e}")
    return None

# Functions to delete entries from tables

# Delete Menu Item
def delete_menu_item(name):
    try:
        item = Menu.objects.get(name=name)
        item.delete()
        print(f"Deleted menu item: {name}")
    except Menu.DoesNotExist:
        print(f"Menu item '{name}' does not exist.")

# Delete Barista by SSN
def delete_barista(ssn):
    try:
        barista = Barista.objects.get(ssn__ssn=ssn)  # Link to Employee SSN
        barista.delete()
        Employee.objects.get(ssn=ssn).delete()  # Delete the Employee as well
        print(f"Deleted barista with SSN {ssn}")
    except ObjectDoesNotExist:
        print(f"Barista with SSN {ssn} does not exist.")

# Delete Manager by SSN
def delete_manager(ssn):
    try:
        manager = Manager.objects.get(ssn__ssn=ssn)  # Link to Employee SSN
        manager.delete()
        Employee.objects.get(ssn=ssn).delete()  # Delete the Employee as well
        print(f"Deleted manager with SSN {ssn}")
    except ObjectDoesNotExist:
        print(f"Manager with SSN {ssn} does not exist.")

# Delete Employee by SSN
def delete_employee(ssn):
    try:
        employee = Employee.objects.get(ssn=ssn)
        employee.delete()
        print(f"Deleted employee with SSN {ssn}")
    except Employee.DoesNotExist:
        print(f"Employee with SSN {ssn} does not exist.")

# Delete Inventory Item by Name
def delete_inventory_item(name):
    try:
        item = InventoryManagement.objects.get(name=name)
        item.delete()
        print(f"Deleted inventory item: {name}")
    except InventoryManagement.DoesNotExist:
        print(f"Inventory item '{name}' does not exist.")

# Delete Promotion by Menu Item
def delete_promotion(menu_name):
    try:
        promo = Promotion.objects.get(menu__name=menu_name)
        promo.delete()
        print(f"Deleted promotion for menu item: {menu_name}")
    except Promotion.DoesNotExist:
        print(f"Promotion for menu item '{menu_name}' does not exist.")

# Delete Sale by Sale ID
def delete_sale(sale_id):
    try:
        sale = Sale.objects.get(id=sale_id)
        sale.delete()
        print(f"Deleted sale with ID {sale_id}")
    except Sale.DoesNotExist:
        print(f"Sale with ID {sale_id} does not exist.")

# Delete Accounting Entry by Day and Time
def delete_account_entry(day, time):
    try:
        entry = Accounting.objects.get(day=day, time=time)
        entry.delete()
        print(f"Deleted accounting entry for {day} at {time}")
    except Accounting.DoesNotExist:
        print(f"No accounting entry found for {day} at {time}.")

# Delete Recipe by Recipe Name
def delete_recipe(recipe_name):
    try:
        Recipe.objects.filter(recipe_name__name=recipe_name).delete()
        print(f"Deleted all recipe entries with name '{recipe_name}'")
    except Exception as e:
        print(f"Error deleting recipe: {e}")