import random

import requests ,json,re
import urllib3,os,secrets,string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout,login
from django.http import HttpResponse
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib import messages
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import csv
import io
from django.shortcuts import render
import uuid
from datetime import datetime
from datetime import datetime, date
from django.utils import timezone
# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def api_call(params, funName):
    api_url = settings.API_URL + funName +"-"+settings.ENVIRONMENT
    response = requests.post(api_url, json=params)
    return response.json()

def users(request):
    if not request.session.get('is_logged_in', False):  # Check session value
        return render(request, 'login.html')
    else:

        params = {}
        user_list = api_call(params, "prismUserslist")
        context = {
            'pageTitle': "USERS LIST",
            'projectName': settings.PROJECT_NAME,
            "user_list": user_list['data']['users'],
            "role_list": user_list['data']['roles'],
        }
    return render(request, 'users.html', context)

def add_user(request):
    # 1. Check login session
    if not request.session.get('is_logged_in'):
        return redirect('login')

    if request.method == "POST":
        try:
            # print(request.POST)  # shows a QueryDict
            # return HttpResponse("OK")

            insertDataArray = []
            # Collect form data

            if request.POST.get("user_id"):
                update_data = {
                    "FistName": request.POST.get("FistName"),
                    "LastName": request.POST.get("LastName"),
                    "role_id": request.POST.get("role_id"),
                    "Password": request.POST.get("Password"),
                    "member_status": request.POST.get("member_status")
                }
                dataList1 = {
                    "updateData": update_data,
                    "table_name": "MEM_USERS",
                    "id_field_name": "ID",
                    "id_field_value": request.POST.get("user_id"),
                }
                api_call(dataList1, "prismMultiplefieldupdate")
            else:
                params = {
                    "username": request.POST.get("EmailID")
                }
                member_exist = api_call(params, "prismAuthentication")
                if member_exist.get('data') and len(member_exist['data']) > 0:
                    messages.error(request, "Username already exists.")
                    return redirect('users')
                else:
                    insert_data = {
                        "FistName": request.POST.get("FistName"),
                        "LastName": request.POST.get("LastName"),
                        "role_id": request.POST.get("role_id"),
                        "EmailID": request.POST.get("EmailID"),
                        "Password": request.POST.get("Password"),
                        "member_status": request.POST.get("member_status")
                    }

                    insertDataArray.append(insert_data)
                    apidata = {
                        "table_name": "MEM_USERS",
                        "insertDataArray": insertDataArray,
                    }
                    insert = api_call(apidata, "prismMultipleinsert")
                    #print(insert)

            return redirect("users")

        except Exception as e:
            # Return error response instead of None
            return HttpResponse(f"Error: {str(e)}", status=500)

    # Handle non-POST case (GET etc.)
    return HttpResponse("Invalid request method", status=405)

