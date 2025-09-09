
import requests ,json,re
import urllib3,os,secrets,string
#from .utils import send_email
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout,login
from django.http import HttpResponse
from datetime import datetime,timedelta
from django.conf import settings
from django.contrib import messages
from django.views.decorators.cache import never_cache, cache_control

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def home(request):
    return HttpResponse("Hello, World!")

def api_call(params, funName):
    api_url = settings.API_URL + funName
    response = requests.post(api_url, json=params)
    return response.json()

def login(request):
    #print('login')
    if request.method == "POST":
        username = request.POST.get('userName')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        #password = psw.strip().replace(" ", "")
        #print(remember_me)
        data = {
            "username": username,
            "password": password
        }

        # Make the API call to 'vegaslogin' endpoint
        try:
            response = requests.post(settings.API_URL + "prismAuthentication", json=data)
            result = response.json()  # Decode the JSON response
            #print(result)

            if response.status_code == 200:
                user_data = result['data']
                if isinstance(user_data, list) and len(user_data) > 0:
                    request.session['user_data'] = user_data[0]
                    request.session['is_logged_in'] = True
                    # if remember_me:
                    #     request.session.set_expiry(1209600)  # 2 weeks (in seconds)
                    # else:
                    #     request.session.set_expiry(0)

                    # insert_data = {
                    #     "employee_id": user_data[0].get('employee_id', None),
                    #     "action": "LOGIN",
                    #     "date_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp
                    # }
                    # # Prepare the dataList dictionary with the table name
                    # data_list = {
                    #     "insertData": insert_data,
                    #     "table_name": "activity_log"
                    # }
                    #
                    # # Make the API call to insert the data into the activity log table
                    # requests.post(settings.API_URL + "vegasinsertdataintable", json=data_list)

                    return redirect('/mywork/')
                    # if request.session['user_data']['employee_role'] == "ZM" or request.session['user_data']['employee_role'] == "ZEM":
                    #     return redirect('/manager_score/')
                    # elif request.session['user_data']['employee_role'] == "RM":
                    #     return redirect('/region_manager_score/')

                else:
                    return render(request, 'login.html', {'error': 'Invalid username or password.'})

            else:
                return HttpResponse({"error": "Failed to sign in user", "details": result}, status=400)

        except requests.exceptions.RequestException as e:
            return HttpResponse({"error": "An error occurred", "details": str(e)}, status=500)

    context = {
        'path': request.path
    }
    # For GET requests, just render the login page
    return render(request, 'login.html',context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def mywork(request):
        if not request.session.get('is_logged_in', False):  # Check session value
            return render(request, 'login.html')
        else:
            return render(request, 'mywork.html')

def logoutuser(request):
    logout(request)
    return redirect('/login')

def memberdetails(request, medicaid_id):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    ## create a api call
    params = {"medicaid_id": medicaid_id}
    member_details = api_call(params,"prismMemberAllDetails")

    return render(request, 'memberdetails.html', {
        "sel_panel_list": member_details['data']['prismMemberAction'],
        "sel_panel_type": member_details['data']['prismMemberActionType'],
        "medicaid_id": medicaid_id,
        "member_details": member_details,
    })

