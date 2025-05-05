from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .models import (
    Barista, Manager, InventoryManagement, Menu,
    Promotion, Sale, Accounting, Recipe
)
from .serializers import (
    BaristaSerializer, ManagerSerializer, InventoryManagementSerializer,
    MenuSerializer, PromotionSerializer, SaleSerializer,
    AccountingSerializer, RecipeSerializer
)


class BaristaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BaristaSerializer

    def get_queryset(self):
        queryset = Barista.objects.all()

        # Access query parameters and filter based on them
        first_name = self.request.query_params.get('first_name', None)
        if first_name:
            queryset = queryset.filter(ssn__first_name__icontains=first_name)

        return queryset


class ManagerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ManagerSerializer

    def get_queryset(self):
        queryset = Manager.objects.all()

        # Access query parameters and filter based on them
        first_name = self.request.query_params.get('first_name', None)
        if first_name:
            queryset = queryset.filter(ssn__first_name__icontains=first_name)

        return queryset


class InventoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = InventoryManagement.objects.all()
    serializer_class = InventoryManagementSerializer

# Handles updating quantity of an item in our inventory
class UpdateInventoryAPIView(APIView):
    def patch(self, request):
        # Checking if our data was sent properly
        print("Received data:", request.data)

        try:
            # Get list of items from request
            order_items = request.data.get("order", [])

            # For each item in orders, add how much product we ordered to our exisitng quantity
            for item in order_items:
                inventory_item = InventoryManagement.objects.get(name=item['name'])
                inventory_item.quantity += item['quantity']
                inventory_item.save()

            return Response({"message": "Inventory updated successfully"})
        except Exception as e:
            return Response({"error": str(e)})


class MenuListCreateAPIView(generics.ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class PromotionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer


class SaleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


class AccountingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Accounting.objects.all()
    serializer_class = AccountingSerializer


class RecipeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()

        # Access query parameters and filter based on them
        recipe_name = self.request.query_params.get('recipe_name', None)
        if recipe_name:
            queryset = queryset.filter(recipe_name__name__icontains=recipe_name)

        return queryset
