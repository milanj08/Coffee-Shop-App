from django.urls import path
from .views import BaristaCreateAPIView

urlpatterns = [
    path('add-barista/', BaristaCreateAPIView.as_view(), name='api_add_barista'),
]