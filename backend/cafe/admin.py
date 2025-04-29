from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Employee, Barista, Menu, Manager, InventoryManagement, Promotion, Sale, Accounting, Recipe, Manages

admin.site.register(Employee)
admin.site.register(Barista)
admin.site.register(Menu)
admin.site.register(Manager)
admin.site.register(InventoryManagement)
admin.site.register(Promotion)
admin.site.register(Sale)
admin.site.register(Accounting)
admin.site.register(Recipe)
admin.site.register(Manages)
