from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Barista
from .serializers import BaristaSerializer


class BaristaCreateAPIView(APIView):
    def post(self, request):
        serializer = BaristaSerializer(data=request.data)
        if serializer.is_valid():
            # Save the barista
            barista = serializer.save()

            # Return the saved data with a success message
            return Response({
                'message': 'Barista added successfully',
                'barista': BaristaSerializer(barista).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
