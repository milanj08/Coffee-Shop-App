from rest_framework import serializers
from .models import Employee, Barista

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['ssn', 'first_name', 'last_name', 'email', 'salary']

class BaristaSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(source='ssn')  # `ssn` is the OneToOneField to Employee

    class Meta:
        model = Barista
        fields = ['employee', 'day', 'start_time', 'end_time']

    def create(self, validated_data):
        employee_data = validated_data.pop('ssn')
        employee = Employee.objects.create(**employee_data)
        barista = Barista.objects.create(ssn=employee, **validated_data)
        return barista