
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
from django.views.decorators.csrf import csrf_exempt

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
    #print(member_details)
    return render(request, 'memberdetails.html', {
        "sel_panel_list": member_details['data']['prismMemberAction'],
        "sel_panel_type": member_details['data']['prismMemberActionType'],
        "member_last_alert": member_details['data']['prismMemberlastalert'],
        "alert_statusList": member_details['data']['prismAlertStatus'],
        "medicaid_id": medicaid_id,
        "member_details": member_details,
    })

@csrf_exempt
def add_action(request):
    # 1. Check login session
    if not request.session.get('is_logged_in'):
        return redirect('login')

    if request.method == "POST":
        try:
            insertDataArray = []
            insertDataArray1 = []

            # Collect form data
            insert_data = {
                "medicaid_id": request.POST.get("medicaid_id"),
                "action_type_source": request.POST.get("action_type_source"),
                "action_id": request.POST.get("action_id"),
                "panel_id": request.POST.get("panel_id"),
                "action_date": request.POST.get("action_date"),
                "action_status": request.POST.get("action_status"),
                "add_by": request.session.get("user_data", {}).get("ID"),
                "action_note": request.POST.get("action_note"),
                "action_result_id": request.POST.get("action_result_id"),
            }
            insertDataArray.append(insert_data)
            apidata = {
                "table_name": "MEM_MEMBER_ACTION_FOLLOW_UP",
                "insertDataArray": insertDataArray,
            }
            api_call(apidata, "prismMultipleinsert")

            insert_data1 = {
                "medicaid_id": request.POST.get("medicaid_id"),
                "action_type": "FOLLOW-UP",
                "log_name": request.POST.get("action_type_source"),
                "log_details": request.POST.get("action_note"),
                "log_status": "SUCCESS",
                "log_by": request.session.get("user_data", {}).get("ID"),
            }
            insertDataArray1.append(insert_data1)
            apidata1 = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1,
            }
            api_call(apidata1, "prismMultipleinsert")

            # ✅ Always return after POST
            medicaid_id = request.POST.get("medicaid_id")
            return redirect("memberdetails", medicaid_id=medicaid_id)

        except Exception as e:
            # ✅ Return error response instead of None
            return HttpResponse(f"Error: {str(e)}", status=500)

    # ✅ Handle non-POST case (GET etc.)
    return HttpResponse("Invalid request method", status=405)

@csrf_exempt
def appointment_add_action(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    try:
        if request.method == "POST":
            insertDataArray = []
            insertDataArray1 = []
            insertDataArray2 = []

            data = {
                # "type": request.POST.get("appointment_action_id"),   # commented in PHP
                "method": request.POST.get("provider_id"),
                "doctor_name": request.POST.get("doctor_name"),
                "vendor_id": request.POST.get("vendor_id"),
                "action_date": request.POST.get("appointment_action_date"),
                "action_time": request.POST.get("appointment_action_time"),
                "status": request.POST.get("appointment_action"),
                "note": request.POST.get("appointment_action_note"),
                "medicaid_id": request.POST.get("appointment_medicaid_id"),
                "place_of_appointment": request.POST.get("place_of_appointment"),
                "added_by": request.session.get("user_data", {}).get("employee_id"),
            }

            insertDataArray.append(data)

            apidata = {
                "table_name": "MEM_SCHEDULE_APPOINTMENT_ACTION",
                "insertDataArray": insertDataArray,
            }
            api_call(apidata, "prismMultipleinsert")

            # ---- log entry ----
            all_log_row = {
                "medicaid_id": request.POST.get("appointment_medicaid_id"),
                # "action_id": idd,
                "action_type": f"Appointment ({request.POST.get('doctor_name')})",
                "log_name": "Appointment",
                "log_details": f"Appointment created for {request.POST.get('appointment_medicaid_id')}",
                "log_status": request.POST.get("appointment_action"),
                "log_by": request.session.get("user_data", {}).get("employee_id"),
            }

            insertDataArray1.append(all_log_row)
            apidata1 = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1,
            }
            api_call(apidata1, "prismMultipleinsert")

            # ---- handle alerts ----
            if request.POST.get("app_alert_id"):
                alert = request.POST.get("app_alert_id").split("/")

                adata = {
                    "alert_status": request.POST.get("app_alert_status_id"),
                    "alert_note": request.POST.get("appointment_action_note"),
                    "created_date": request.POST.get("appointment_action_date"),
                }

                dataList1 = {
                    "updateData": adata,
                    "table_name": "MEM_ALERTLIST",
                    "id_field_name": "id",
                    "id_field_value": alert[1],
                }
                api_call(dataList1, "prismMultiplefieldupdate")

                all_log_row1 = {
                    "medicaid_id": request.POST.get("appointment_medicaid_id"),
                    "action_id": alert[0],
                    "action_type": "Appointment scheduled",
                    "log_name": f"Alert ({request.POST.get('app_alertname')})",
                    "log_details": request.POST.get("appointment_action_note"),
                    "log_status": "Completed",
                    "log_by": request.session.get("user_data", {}).get("employee_id"),
                    "log_type": "Alert",
                }

                insertDataArray2.append(all_log_row1)
                apidata2 = {
                    "table_name": "MEM_SYSTEM_LOG",
                    "insertDataArray": insertDataArray2,
                }
                api_call(apidata2, "prismMultipleinsert")

                # update outreach member status
                alert_name = request.POST.get("app_alertname").split("(")
                if alert[0] == "5":
                    updata = {"CONTACT_STATUS": "Completed"}
                else:
                    updata = {alert_name[0].strip(): "Completed"}

                dataList2 = {
                    "updateData": updata,
                    "table_name": "MEM_OUTREACH_MEMBERS",
                    "id_field_name": "medicaid_id",
                    "id_field_value": data["medicaid_id"],
                }
                api_call(dataList2, "prismMultiplefieldupdate")

    except Exception as e:
        return HttpResponse(str(e), status=500)

    return redirect("memberdetails", medicaid_id=request.POST.get("appointment_medicaid_id"))

