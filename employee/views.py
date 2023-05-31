from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import *
from django.db import connection
from django.apps import apps
import json
import re


def convert_to_json(form_data):
    pattern = r'name="(.*?)"\r\n\r\n(.*?)\r\n'
    matches = re.findall(pattern, form_data.decode())

    # Convert the matches into a dictionary
    data_dict = {key: value for key, value in matches}

    # Convert the dictionary to JSON
    # json_data = json.dumps(data_dict)

    return(data_dict)


def add_employee_data_to_db(fname, lname, email, phone, address):
    with connection.cursor() as cursor:
        query = "INSERT INTO employee_employeemodel (first_name, last_name, email, phone, address) VALUES (%s, %s, %s, %s, %s)"
        values = (fname, lname, email, phone, address)
        cursor.execute(query, values)
        connection.commit()


class EmployeeView(View):
    template_name = "employee.html"

    def get(self, request, emp_id=0):
        if emp_id != 0:
            employee = EmployeeModel.objects.raw("SELECT id, first_name, last_name, email, phone, address FROM "
                                                 "employee_employeemodel WHERE id = {}".format(emp_id))
            return render(request, 'employee_update.html', {'employees': employee})
        else:
            employee = EmployeeModel.objects.raw("SELECT * FROM employee_employeemodel")
            return render(request, self.template_name, {'employees': employee})

    def delete(self, request):
        id = request.GET['id']
        employee = EmployeeModel.objects.raw("DELETE FROM employee_employeemodel WHERE id = {}".format(id))
        return render(request, self.template_name, {'employees': employee})

    def put(self, request, emp_id):
        data = convert_to_json(request.body)
        employee = EmployeeModel.objects.raw("UPDATE employee_employeemodel SET first_name = '{}', last_name = '{}',"
                                             " email = '{}', phone = '{}', address = '{}' WHERE id = {}".format(data['fname'],
                                                data['lname'], data['email'], data['phone'], data['address'], emp_id))
        return JsonResponse({"status": "success"})

    def post(self, request, *args, **kwargs):
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        address = request.POST["address"]
        add_employee_data_to_db(fname, lname, email, phone, address)
        employee = EmployeeModel.objects.raw("SELECT * FROM employee_employeemodel")
        return render(request, self.template_name, {'employees': employee})