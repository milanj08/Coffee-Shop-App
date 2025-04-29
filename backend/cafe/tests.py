import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.test import TestCase
from .services import add_menu_item
from .models import Menu

# Create your tests here
class AddMenuItemTestCase(TestCase):

    def test_add_menu_item(self):
        # Call the add_menu_item function to add a new menu item
        menu_item = add_menu_item("Latte", 350, "coffee", 4.50, "hot")

        # Assert that the menu item was created and exists in the database
        self.assertIsNotNone(menu_item)  # Ensure the item was returned (created)

        # Check if the item was saved in the database
        saved_item = Menu.objects.get(name="Latte")

        # Assert that the details match
        self.assertEqual(saved_item.name, "Latte")
        self.assertEqual(saved_item.size, 350)
        self.assertEqual(saved_item.price, 4.50)
        self.assertEqual(saved_item.hot_cold, "hot")
