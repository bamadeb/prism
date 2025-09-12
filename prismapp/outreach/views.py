
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
        # print(request.session.get('user_data'))
        user_data = request.session.get('user_data')
        if user_data:  # make sure it exists
            user_id = user_data.get('ID')
        data = {
            "user_id": user_id
        }
        try:
            response = requests.post(settings.API_URL + "prismAllmyworkspace", json=data)
            myWorkSpaceResult = response.json()  # Decode the JSON response
        except requests.exceptions.RequestException as e:
            return HttpResponse({"error": "An error occurred", "details": str(e)}, status=500)
        myWorkAllSpace = myWorkSpaceResult['data']
        from datetime import datetime, date

        today = date.today()
        task_list = myWorkAllSpace['taskList']

        for task in task_list:
            ad = task.get("action_date")
            if isinstance(ad, str):
                try:
                    # Parse ISO 8601 string
                    task["action_date"] = datetime.fromisoformat(ad.replace("Z", "+00:00")).date()
                except ValueError:
                    task["action_date"] = None
            action_date = task.get("action_date")

            if action_date:
                # If it's a string, convert it to date
                if isinstance(action_date, str):
                    try:
                        # Adjust format depending on your actual data (YYYY-MM-DD assumed here)
                        action_date = datetime.strptime(action_date, "%Y-%m-%d").date()
                        task["action_date"] = datetime.fromisoformat(ad.replace("Z", "+00:00")).date()
                    except ValueError:
                        # Skip if invalid format
                        task["color"] = "#fff"
                        continue

                # Now safe to compare
                if action_date < today and task.get("status") not in ["Successful", "Close", "N/A"]:
                    task["color"] = "red"
                else:
                    task["color"] = "#fff"
            else:
                task["color"] = "#fff"

        members_list = myWorkAllSpace['members']
        alertListMember = myWorkAllSpace['alertList']
        curdate = datetime.now().date()  # current date without time
        for member in members_list:
            #print(member)
            alertCount = 0
            for memberAlert in alertListMember:
                due_date = datetime.fromisoformat(memberAlert["due_date"].replace("Z", "+00:00")).date()
                if member["medicaid_id"] == memberAlert["medicaid_id"] and curdate <= due_date:
                    alertCount += 1
            member["alertCount"] = alertCount
            elig_exp_dt = member.get("ELIG_EXP_DT")
            if elig_exp_dt:
                member["ELIG_EXP_DT"] = datetime.fromisoformat(elig_exp_dt.replace("Z", "+00:00")).date()
            else:
                member["ELIG_EXP_DT"] = None
            third_last_action_date = member.get("third_last_action_date")
            if third_last_action_date:
                member["third_last_action_date"] = datetime.fromisoformat(
                    third_last_action_date.replace("Z", "+00:00")).date()
            else:
                member["third_last_action_date"] = None
            second_last_action_date = member.get("second_last_action_date")
            if second_last_action_date:
                member["second_last_action_date"] = datetime.fromisoformat(
                    second_last_action_date.replace("Z", "+00:00")).date()
            else:
                member["second_last_action_date"] = None
            last_action_date = member.get("last_action_date")
            if last_action_date:
                member["last_action_date"] = datetime.fromisoformat(last_action_date.replace("Z", "+00:00")).date()
            else:
                member["last_action_date"] = None
            recentActivity = myWorkAllSpace['recentActivity']
            for activity in recentActivity:
                #print(activity)
                add_date = activity.get("add_date")
                if isinstance(add_date, str):
                    activity["add_date"] = datetime.fromisoformat(add_date.replace("Z", "+00:00"))

        alertList = myWorkAllSpace['alertList']
        for alert in alertList:
            #print(activity)
            due_date = alert.get("due_date")
            if isinstance(due_date, str) and due_date:
                # Convert ISO string to datetime
                dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                alert["due_date"] = dt  # keep as datetime object
        print(members_list)
        context = {
            'members': members_list,
            'pageTitle': "My Work",
            'alertCount': 1,
            'today': date.today(),
            'alert_count': myWorkAllSpace['alertCount'],
            'alertList': alertList,
            'kpis_data': myWorkAllSpace['kpisData'],
            'task_list': task_list,
            'refared_member_list': myWorkAllSpace['referrerList'],
            'sel_panel_list': myWorkAllSpace['prismMemberAction'],
            'sel_panel_type': myWorkAllSpace['prismMemberActionType'],
            'roleList': myWorkAllSpace['prismRoleList'],
            'plan_list': myWorkAllSpace['prismPlanlist'],
            'all_3day_transport_list': myWorkAllSpace['transportList'],
            'recent_activity': recentActivity,
            'prismWorkspacekpi': myWorkAllSpace['prismWorkspacekpi']
        }
    #print(myWorkAllSpace)
    # print(request.session.get('user_data', {}).get('ID'))
    return render(request, 'mywork.html', context)

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
def memberhistory(request, medicaid_id):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    ## create a api call
    params = {"medicaid_id": medicaid_id}
    historyResponse = api_call(params,"prismMemberhistory")
    #print(historyResponse)
    roadmap_data = []
    roadmap_data_str = ''
    for roadmap in historyResponse.get("data", {}).get("roadmap_member_log", []):

        try:
            #print(roadmap["add_date"])
            add_date = datetime.strptime(roadmap["add_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            add_date = add_date - timedelta(days=30)

        except Exception as e:
            #print("Error message:", e)  # Only the error message
            #print("Error type:", type(e))  # The type of error
            #print("Full details:", repr(e))  # Full exception representation
            continue

        roadmap_data.append(
            f"""{{
                x: Date.UTC({add_date.year}, {add_date.month - 1}, {add_date.day}),
                name: '{roadmap["log_name"]}',
                label: '',
                description: '{roadmap["log_details"]}'
            }}"""
        )
        roadmap_data_str = ",".join(roadmap_data)
    member_log = historyResponse['data']['roadmap_member_log']
    for activity in member_log:
        # print(activity)
        add_date = activity.get("add_date")
        if isinstance(add_date, str):
            activity["add_date"] = datetime.fromisoformat(add_date.replace("Z", "+00:00"))

    #print(historyResponse['data']['roadmap_member_log'])
    return render(request, 'memberhistory.html', {
        "member_details": historyResponse['data']['member_details'],
        'pageTitle': "MEMBER HISTORY",
        "claim_details": historyResponse['data']['claim_details'],
        "log_type_list": historyResponse['data']['log_type_list'],
        "medicaid_id": medicaid_id,
        "roadmap_member_log": member_log,
        "roadmap_data_str": roadmap_data_str,
    })

