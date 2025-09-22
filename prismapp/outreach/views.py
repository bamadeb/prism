import random

import requests ,json,re
import urllib3,os,secrets,string
#from .utils import send_email
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
        'path': request.path,
        'projectName': settings.PROJECT_NAME,
        'pageTitle': 'LOGIN',
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
            #################
            #now = timezone.now()  # gets current datetime with timezone support
            #print("Step 2 - 1st API Call Start:", now)  # prints in console
            ################
            #response = requests.post(settings.API_URL + "prismAllmyworkspace", json=data)

            response = requests.post(settings.API_URL + "prismOutreachAllmyworkspaceSP", json=data)
            #################
            #now = timezone.now()  # gets current datetime with timezone support
            #print("Step 3  - 2st API Call Start:", now)  # prints in console
            ################

            myWorkSpaceResult = response.json()  # Decode the JSON response
            #print(myWorkSpaceResult)
            # overallSummary = requests.post(settings.API_URL + "prismRiskQualitySummary", json={})
            # #################
            # now = timezone.now()  # gets current datetime with timezone support
            # print("Step 4  - 3st API Call Start:", now)  # prints in console
            # ################
            #
            # overallSummaryResult = overallSummary.json()  # Decode the JSON response
            # ownSummary = requests.post(settings.API_URL + "prismRiskQualitySummary", json=data)
            # #################
            # now = timezone.now()  # gets current datetime with timezone support
            # print("Step 5  - 4st API Call Start:", now)  # prints in console
            # ################
            #
            # ownSummaryResult = ownSummary.json()  # Decode the JSON response
            # performancSummary = requests.post(settings.API_URL + "prismPriorityAndOtherPerformancSummary", json=data)
            # #################
            # now = timezone.now()  # gets current datetime with timezone support
            # print("Step 6  - All API call end:", now)  # prints in console
            # ################
            #
            # performancSummaryResult = performancSummary.json()  # Decode the JSON response
            #print(performancSummaryResult)
        except requests.exceptions.RequestException as e:
            return HttpResponse({"error": "An error occurred", "details": str(e)}, status=500)
        #################
        #now = timezone.now()  # gets current datetime with timezone support
        #print("Step 7  - Data processing start:", now)  # prints in console
        ################
        myWorkAllSpace = myWorkSpaceResult['data']
        #print(myWorkAllSpace['priorityAndOtherPerformanceSummary'])
        performanc = myWorkAllSpace['priorityAndOtherPerformanceSummary']
        performancArray = []
        totalArray = {
            'total_priority_count': 0,
            'total_call_count': 0,
            'total_other_call_count': 0,
            'total_other_count': 0,
            'total_priority_complete_gaps_count': 0,
            'total_priority_gaps_count': 0,
            'total_other_gaps_count': 0,
            'total_other_complete_gaps_count': 0,
            'priority_call_percentage': 0,
            'other_call_percentage': 0,
            'priority_gaps_percentage': 0,
            'other_gaps_percentage': 0,
            'priority_pcp_visit_count': 0,
            'other_pcp_visit_count': 0,
            'priority_call_color': '',
            'other_call_color': '',
            'priority_gaps_color': '',
            'other_gaps_color': '',
            'priority_pcp_visit_color': '',
            'other_pcp_visit_color': ''
        }

        for item in performanc:
            pcp_id = item["PCP_TAX_ID"]
            values = {k: v for k, v in item.items() if k != "PCP_TAX_ID"}
            # Get safe numbers
            call_count = float(values.get("call_count", 0) or 0)
            priority_count = float(values.get("priority_count", 0) or 0)
            totalArray['total_priority_count'] += priority_count
            totalArray['total_call_count'] += call_count
            # Calculate percentage
            values["priority_percentage"] = round((call_count / priority_count) * 100, 2) if priority_count > 0 else 0
            if values["priority_percentage"] < 60:
                values["priority_color"] = "red"
            elif values["priority_percentage"] < 80:
                values["priority_color"] = "#FFAE42"
            else:
                values["priority_color"] = "green"
            # Get safe numbers
            other_call_count = float(values.get("other_call_count", 0) or 0)
            other_count = float(values.get("other_count", 0) or 0)
            totalArray['total_other_call_count'] += other_call_count
            totalArray['total_other_count'] += other_count
            # Calculate percentage
            values["other_call_percentage"] = round((other_call_count / other_count) * 100, 2) if other_count > 0 else 0
            if values["other_call_percentage"] < 60:
                values["other_call_color"] = "red"
            elif values["other_call_percentage"] < 80:
                values["other_call_color"] = "#FFAE42"
            else:
                values["other_call_color"] = "green"
            priority_complete_gaps_count = float(values.get("priority_complete_gaps_count", 0) or 0)
            priority_gaps_count = float(values.get("priority_gaps_count", 0) or 0)
            totalArray['total_priority_complete_gaps_count'] += priority_complete_gaps_count
            totalArray['total_priority_gaps_count'] += priority_gaps_count
            # Calculate percentage
            values["priority_gaps_percentage"] = round((priority_complete_gaps_count / priority_gaps_count) * 100, 2) if priority_gaps_count > 0 else 0
            if values["priority_gaps_percentage"] < 60:
                values["priority_gaps_color"] = "red"
            elif values["priority_gaps_percentage"] < 80:
                values["priority_gaps_color"] = "#FFAE42"
            else:
                values["priority_gaps_color"] = "green"
            other_gaps_count = float(values.get("other_gaps_count", 0) or 0)
            other_complete_gaps_count = float(values.get("other_complete_gaps_count", 0) or 0)
            totalArray['total_other_gaps_count'] += other_gaps_count
            totalArray['total_other_complete_gaps_count'] += other_complete_gaps_count
            # Calculate percentage
            values["other_gaps_percentage"] = round((other_complete_gaps_count / other_gaps_count) * 100, 2) if other_gaps_count > 0 else 0
            if values["other_gaps_percentage"] < 60:
                values["other_gaps_color"] = "red"
            elif values["other_gaps_percentage"] < 80:
                values["other_gaps_color"] = "#FFAE42"
            else:
                values["other_gaps_color"] = "green"
            # Get safe numbers for PCP visit
            priority_pcp_visit_count = float(values.get("priority_pcp_visit_count", 0) or 0)
            priority_count = float(values.get("priority_count", 0) or 0)
            #totalArray['total_priority_count'] += priority_count
            totalArray['priority_pcp_visit_count'] += priority_pcp_visit_count
            # Calculate percentage other_count
            values["priority_pcp_visit_percentage"] = round((priority_pcp_visit_count / priority_count) * 100, 2) if priority_count > 0 else 0
            if values["priority_pcp_visit_percentage"] < 60:
                values["priority_pcp_visit_color"] = "red"
            elif values["priority_pcp_visit_percentage"] < 80:
                values["priority_pcp_visit_color"] = "#FFAE42"
            else:
                values["priority_pcp_visit_color"] = "green"
            # Get safe numbers for PCP visit
            other_pcp_visit_count = float(values.get("other_pcp_visit_count", 0) or 0)
            priority_count = float(values.get("priority_count", 0) or 0)
            #totalArray['total_priority_count'] += priority_count
            totalArray['other_pcp_visit_count'] += other_pcp_visit_count
            # Calculate percentage other_count
            values["other_pcp_visit_percentage"] = round((other_pcp_visit_count / other_count) * 100, 2) if other_count > 0 else 0
            if values["other_pcp_visit_percentage"] < 60:
                values["other_pcp_visit_color"] = "red"
            elif values["other_pcp_visit_percentage"] < 80:
                values["other_pcp_visit_color"] = "#FFAE42"
            else:
                values["other_pcp_visit_color"] = "green"

            performancArray.append({pcp_id: values})

        totalArray['priority_call_percentage'] = round((totalArray['total_call_count'] / totalArray['total_priority_count']) * 100, 2) if totalArray['total_priority_count'] > 0 else 0
        totalArray['other_call_percentage'] = round((totalArray['total_other_call_count'] / totalArray['total_other_count']) * 100, 2) if totalArray['total_other_count'] > 0 else 0
        totalArray['priority_gaps_percentage'] = round((totalArray['total_priority_complete_gaps_count'] / totalArray['total_priority_gaps_count']) * 100, 2) if totalArray['total_priority_gaps_count'] > 0 else 0
        totalArray['other_gaps_percentage'] = round((totalArray['total_other_complete_gaps_count'] / totalArray['total_other_gaps_count']) * 100, 2) if totalArray['total_other_gaps_count'] > 0 else 0
        totalArray['priority_pcp_percentage'] = round((totalArray['priority_pcp_visit_count'] / totalArray['total_priority_count']) * 100, 2) if totalArray['total_priority_count'] > 0 else 0
        totalArray['other_pcp_percentage'] = round((totalArray['other_pcp_visit_count'] / totalArray['total_other_count']) * 100, 2) if totalArray['total_other_count'] > 0 else 0
        if totalArray['priority_call_percentage'] < 60:
            totalArray["priority_call_color"] = "red"
        elif totalArray['priority_call_percentage'] < 80:
            totalArray["priority_call_color"] = "#FFAE42"
        else:
            totalArray["priority_call_color"] = "green"
        if totalArray['other_call_percentage'] < 60:
            totalArray["other_call_color"] = "red"
        elif totalArray['other_call_percentage'] < 80:
            totalArray["other_call_color"] = "#FFAE42"
        else:
            totalArray["other_call_color"] = "green"
        if totalArray['priority_gaps_percentage'] < 60:
            totalArray["priority_gaps_color"] = "red"
        elif totalArray['priority_gaps_percentage'] < 80:
            totalArray["priority_gaps_color"] = "#FFAE42"
        else:
            totalArray["priority_gaps_color"] = "green"
        if totalArray['other_gaps_percentage'] < 60:
            totalArray["other_gaps_color"] = "red"
        elif totalArray['other_gaps_percentage'] < 80:
            totalArray["other_gaps_color"] = "#FFAE42"
        else:
            totalArray["other_gaps_color"] = "green"
        if totalArray['priority_pcp_percentage'] < 60:
            totalArray["priority_pcp_color"] = "red"
        elif totalArray['priority_pcp_percentage'] < 80:
            totalArray["priority_pcp_color"] = "#FFAE42"
        else:
            totalArray["priority_pcp_color"] = "green"
        if totalArray['other_pcp_percentage'] < 60:
            totalArray["other_pcp_color"] = "red"
        elif totalArray['other_pcp_percentage'] < 80:
            totalArray["other_pcp_color"] = "#FFAE42"
        else:
            totalArray["other_pcp_color"] = "green"

        #print(totalArray)

        #print(overallSummaryResult)
        #today = date.today()

        # task_list = myWorkAllSpace['taskList']
        #
        # for task in task_list:
        #     ad = task.get("action_date")
        #     if isinstance(ad, str):
        #         try:
        #             # Parse ISO 8601 string
        #             task["action_date"] = datetime.fromisoformat(ad.replace("Z", "+00:00")).date()
        #         except ValueError:
        #             task["action_date"] = None
        #     action_date = task.get("action_date")
        #
        #     if action_date:
        #         # If it's a string, convert it to date
        #         if isinstance(action_date, str):
        #             try:
        #                 # Adjust format depending on your actual data (YYYY-MM-DD assumed here)
        #                 action_date = datetime.strptime(action_date, "%Y-%m-%d").date()
        #                 task["action_date"] = datetime.fromisoformat(ad.replace("Z", "+00:00")).date()
        #             except ValueError:
        #                 # Skip if invalid format
        #                 task["color"] = "#fff"
        #                 continue
        #
        #         # Now safe to compare
        #         if action_date < today and task.get("status") not in ["Successful", "Close", "N/A"]:
        #             task["color"] = "red"
        #         else:
        #             task["color"] = "#fff"
        #     else:
        #         task["color"] = "#fff"

        members_list = myWorkAllSpace['members']
        #alertListMember = myWorkAllSpace['alertList']
        #curdate = datetime.now().date()  # current date without time
        # for member in members_list:
        #     #print(member)
        #     alertCount = 0
        #     for memberAlert in alertListMember:
        #         due_date = datetime.fromisoformat(memberAlert["due_date"].replace("Z", "+00:00")).date()
        #         if member["medicaid_id"] == memberAlert["medicaid_id"] and curdate <= due_date:
        #             alertCount += 1
        #     member["alertCount"] = alertCount
        #     elig_exp_dt = member.get("ELIG_EXP_DT")
        #     if elig_exp_dt:
        #         member["ELIG_EXP_DT"] = datetime.fromisoformat(elig_exp_dt.replace("Z", "+00:00")).date()
        #     else:
        #         member["ELIG_EXP_DT"] = None
        #     third_last_action_date = member.get("third_last_action_date")
        #     if third_last_action_date:
        #         member["third_last_action_date"] = datetime.fromisoformat(
        #             third_last_action_date.replace("Z", "+00:00")).date()
        #     else:
        #         member["third_last_action_date"] = None
        #     second_last_action_date = member.get("second_last_action_date")
        #     if second_last_action_date:
        #         member["second_last_action_date"] = datetime.fromisoformat(
        #             second_last_action_date.replace("Z", "+00:00")).date()
        #     else:
        #         member["second_last_action_date"] = None
        #     last_action_date = member.get("last_action_date")
        #     if last_action_date:
        #         member["last_action_date"] = datetime.fromisoformat(last_action_date.replace("Z", "+00:00")).date()
        #     else:
        #         member["last_action_date"] = None
        recentActivity = myWorkAllSpace['recentActivity']
        for activity in recentActivity:
            #print(activity)
            add_date = activity.get("add_date")
            if isinstance(add_date, str):
                activity["add_date"] = datetime.fromisoformat(add_date.replace("Z", "+00:00"))

        # alertList = myWorkAllSpace['alertList']
        # for alert in alertList:
        #     #print(activity)
        #     due_date = alert.get("due_date")
        #     if isinstance(due_date, str) and due_date:
        #         # Convert ISO string to datetime
        #         dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        #         alert["due_date"] = dt  # keep as datetime object
        #print(members_list)
        #################
        #now = timezone.now()  # gets current datetime with timezone support
        #print("Step 7  - Data processing end:", now)  # prints in console
        ################
        #print(myWorkAllSpace['overallRiskQualitySummary'])
        #print(myWorkAllSpace['ownRiskQualitySummary'])
        context = {
            'members': members_list,
            'pageTitle': "MY WORKSPACE",
            'projectName': settings.PROJECT_NAME,
            'alertCount': 1,
            'today': date.today(),
            #'alert_count': myWorkAllSpace['alertCount'],
            #'alertList': alertList,
            #'kpis_data': myWorkAllSpace['kpisData'],
            #'task_list': task_list,
            #'refared_member_list': myWorkAllSpace['referrerList'],
            #'sel_panel_list': myWorkAllSpace['prismMemberAction'],
            #'sel_panel_type': myWorkAllSpace['prismMemberActionType'],
            #'roleList': myWorkAllSpace['prismRoleList'],
            #'plan_list': myWorkAllSpace['prismPlanlist'],
            #'all_3day_transport_list': myWorkAllSpace['transportList'],
            'recent_activity': recentActivity,
            #'prismWorkspacekpi': myWorkAllSpace['prismWorkspacekpi'],
            'overallSummary': myWorkAllSpace['overallRiskQualitySummary'],
            'ownSummary': myWorkAllSpace['ownRiskQualitySummary'],
            'performancArray': performancArray,
            'totalArray': totalArray
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
    birth_date = None
    member_details = api_call(params,"prismMemberAllDetails")

    paramslist = {"medicaid_id": medicaid_id, "PROCESS_STATUS": "0"}
    ## create a api call
    gap_list = api_call(paramslist, "prismGetgapList")
    quality_list = api_call(paramslist, "prismGetqualityList")
    #print(gap_list)

    log_details = []
    if len(member_details) > 0:
        for log in member_details['data']['logDetails']:
            # Convert string to datetime
            log["add_date"] = datetime.fromisoformat(log["add_date"].replace("Z", "+00:00"))
            log_details.append(log)

    member_alertList = []
    for member in member_details['data']['alertList']:
        # Convert string to datetime
        member["due_date"] = datetime.fromisoformat(member["due_date"].replace("Z", "+00:00"))
        member_alertList.append(member)

    medical_claim_details = []
    for claim in member_details['data']['medicalClaim']:
        # Convert string to datetime
        dt = datetime.fromisoformat(claim["FIRST_DOS"].replace("Z", "+00:00"))
        # Format as m/d/Y
        claim["FIRST_DOS"] = dt.strftime("%m/%d/%Y")
        medical_claim_details.append(claim)

    gift_details = []
    for gift in member_details['data']['prismGiftcard']:
        # Convert ISO string (with Zulu timezone) to datetime
        gift["DATE_OF_SERVICE"] = datetime.fromisoformat(gift["DATE_OF_SERVICE"].replace("Z", "+00:00"))
        gift_details.append(gift)

    rx_claim_details = []
    for rx in member_details['data']['prismRxClaimsNew']:
        # Convert ISO string (with Zulu timezone) to datetime
        rx["Service_Date"] = datetime.fromisoformat(rx["Service_Date"].replace("Z", "+00:00"))
        rx_claim_details.append(rx)

    hedis_key_array = []
    hedis_non_complant_count_array = {}
    hedis_rows = []

    for member_hedis in member_details['data']['hedisDetails']:
        non_complant_count = 0

        for key, hvalue in member_hedis.items():
            if hvalue:
                if hvalue == "Non-Compliant":
                    non_complant_count += 1

                if key not in hedis_key_array:
                    hedis_key_array.append(key)

        year = member_hedis["Year"]
        month = member_hedis["Month"]
        if year not in hedis_non_complant_count_array:
            hedis_non_complant_count_array[year] = {}
        hedis_non_complant_count_array[year][month] = non_complant_count

        for member in member_details['data']['hedisDetails']:
            row = []
            for idx, key in enumerate(hedis_key_array, start=1):
                value = member.get(key, "")
                color = ""

                # coloring rules
                if key == "# Compliant" or value == "Compliant":
                    color = "color: #008000;"
                elif value == "Non-Compliant":
                    color = "color: #FF0000;"

                # insert "# Non-Compliant" column before 3rd column
                if idx == 3:
                    non_compliant_count = hedis_non_complant_count_array.get(
                        member["Year"], {}
                    ).get(member["Month"], 0)
                    row.append({"value": non_compliant_count, "color": "color: #FF0000;"})

                # add the normal column
                row.append({"value": value, "color": color})
            hedis_rows.append(row)

            birth_str = member_details['data']['memberDetails'][0].get("BIRTH")
            birth_date = None
            if birth_str:
                try:
                    birth_date = datetime.strptime(birth_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                except ValueError:
                    pass



    return render(request, 'memberdetails.html', {
        'pageTitle': "MEMBER DETAILS",
        'projectName': settings.PROJECT_NAME,
        "sel_panel_list": member_details['data']['prismMemberAction'],
        "sel_panel_type": member_details['data']['prismMemberActionType'],
        "member_last_alert": member_details['data']['prismMemberlastalert'],
        "alert_statusList": member_details['data']['prismAlertStatus'],
        "alertList": member_details['data']['prismAlertMaster'],
        "member_details": member_details['data']['memberDetails'],
        "assign_to_user": member_details['data']['prismUsers'],
        "alt_address": member_details['data']['altaddress'],
        "member_alt_phone_details": member_details['data']['prismMemberaltphone'],
        "all_language_master_list": member_details['data']['prismMasterLanguage'],
        "member_alt_language_details": member_details['data']['prismMemberaltlanguage'],
        "pcp_list": member_details['data']['prismMemberPCPList'],
        "medical_claim_details": member_details['data']['medicalClaim'],
        "risk_details": member_details['data']['prismMembershiprisk'],
        "problem_list": member_details['data']['prismCrispProblems'],
        "encounters": member_details['data']['prismCrispEncounters'],
        "immunizations": member_details['data']['prismCrispImmunization'],
        "medications": member_details['data']['prismCrispMedication'],
        "insurance_provider": member_details['data']['prismCrispInsuranceProvider'],
        "prism_claim_details": member_details['data']['prismPrismClaim'],
        "gap_list": gap_list['data'],
        "quality_list": quality_list['data'],
        "rx_claim_details": rx_claim_details,
        "hedis_rows": hedis_rows,
        "gift_details": gift_details,
        "hedis_non_complant_count_array": hedis_non_complant_count_array,
        "hedis_key_array": hedis_key_array,
        "member_alertList": member_alertList,
        "log_details": log_details,
        "birth_date": birth_date,
        "medicaid_id": medicaid_id,
    })

@csrf_exempt
def add_action(request):
    # 1. Check login session
    if not request.session.get('is_logged_in'):
        return redirect('login')

    if request.method == "POST":
        try:
            # print(request.POST)
            # return HttpResponse("Not allowed")

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
                "action_type": request.POST.get("action_type_name"),
                "log_name": request.POST.get("action_type_source"),
                "log_details": request.POST.get("action_note"),
                "log_status": request.POST.get("action_status"),
                "log_by": request.session.get("user_data", {}).get("ID"),
            }
            insertDataArray1.append(insert_data1)
            apidata1 = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1,
            }
            api_call(apidata1, "prismMultipleinsert")

            ##### update quality data
            quality_ids = request.POST.getlist("quality_id")
            for qid in quality_ids:
                qualityupdate = {"id": qid}
                api_call(qualityupdate, "prismUpdatequalityStatus")

            ##### update gap data
            gap_ids = request.POST.getlist("gap_id")
            for gid in gap_ids:
                paramsupdate = {"id": gid}
                api_call(paramsupdate, "prismUpdategapStatus")

            # Always return after POST
            medicaid_id = request.POST.get("medicaid_id")
            return redirect("memberdetails", medicaid_id=medicaid_id)

        except Exception as e:
            # Return error response instead of None
            return HttpResponse(f"Error: {str(e)}", status=500)

    # Handle non-POST case (GET etc.)
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
                "added_by": request.session.get("user_data", {}).get("ID"),
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
                "log_by": request.session.get("user_data", {}).get("ID"),
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
                    "log_by": request.session.get("user_data", {}).get("ID"),
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
        'projectName': settings.PROJECT_NAME,
        "claim_details": historyResponse['data']['claim_details'],
        "log_type_list": historyResponse['data']['log_type_list'],
        "medicaid_id": medicaid_id,
        "roadmap_member_log": member_log,
        "roadmap_data_str": roadmap_data_str,
    })

@require_POST
def member_add_update_alert(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    try:
        alert_list_id = request.POST.get("alert_list_id")
        if not alert_list_id:
            # Insert mode
            adata = {
                "medicaid_id": request.POST.get("member_id"),
                "alert_id": request.POST.get("alert_id"),
                "alert_type": request.POST.get("alert_type_id"),
                "alert_status": request.POST.get("alert_status_id"),
                "alert_assign_user": request.POST.get("assign_user_id"),
                "alert_note": request.POST.get("alert_note"),
                "created_date": request.POST.get("created_date"),
                "due_date": request.POST.get("due_date"),
                "added_by": request.session.get("user_data", {}).get("ID"),
            }

            # If completed
            if adata["alert_status"] in ["28", "5"]:
                adata["completed_date"] = datetime.today().strftime("%Y-%m-%d")

            insertDataArray = [adata]
            params = {
                "table_name": "MEM_ALERTLIST",
                "insertDataArray": insertDataArray,
            }
            #print(params)

            # API call
            api_call(params, "prismMultipleinsert")

        else:
            # Update mode
            bdata = {
                "alert_type": request.POST.get("alert_type_id"),
                "alert_status": request.POST.get("alert_status_id"),
                "alert_assign_user": request.POST.get("assign_user_id") or 0,
                "alert_note": request.POST.get("alert_note"),
                "created_date": request.POST.get("created_date"),
                "due_date": request.POST.get("due_date"),
            }

            # If completed
            if bdata["alert_status"] in ["28", "5"]:
                bdata["completed_date"] = datetime.today().strftime("%Y-%m-%d")

            params = {
                "updateData": bdata,
                "table_name": "MEM_ALERTLIST",
                "id_field_name": "id",
                "id_field_value": alert_list_id,
            }
            # API call
            api_call(params, "prismMultiplefieldupdate")

        # Insert into system log
        all_log = {
            "medicaid_id": request.POST.get("member_id"),
            "action_id": alert_list_id,
            "alert_status_id": request.POST.get("alert_status_id"),
            "alert_status": 1,
            "log_name": "Alert",
            "log_details": request.POST.get("alert_note"),
            "log_status": request.POST.get("alert_status_txt"),
            "log_by": request.session.get("user_data", {}).get("ID"),
            "roadmap_flag": 1,
            "action_type": request.POST.get("alert_type_txt"),
        }

        insertDataArray1 = [all_log]
        params = {
            "table_name": "MEM_SYSTEM_LOG",
            "insertDataArray": insertDataArray1,
        }
        # API call
        api_call(params, "prismMultipleinsert")

    except Exception as e:
        return redirect("error_page")  # Or handle error gracefully

    return redirect("memberdetails", medicaid_id=request.POST.get("member_id"))


def add_member_alt_address(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    try:
        if request.method == "POST":
            medicaid_id = request.POST.get("medicaid_id")
            # Data for address table
            insertDataArray = [{
                "medicaid_id": request.POST.get("medicaid_id"),
                "alt_address": request.POST.get("alt_address"),
                "alt_city": request.POST.get("alt_city"),
                "alt_state": request.POST.get("alt_state"),
                "alt_zip": request.POST.get("alt_zip"),
                "add_by": request.session.get("user_data", {}).get("ID"),
            }]
            params = {
                "table_name": "MEM_ALT_ADDRESS",
                "insertDataArray": insertDataArray
            }
            #print(params)
            # API call
            api_call(params, "prismMultipleinsert")

            # Data for system log table
            insertDataArray1 = [{
                "medicaid_id": medicaid_id,
                "action_type": "Address changed",
                "log_name": "Alternative Address",
                "log_details": f"Alternative Address changed for {medicaid_id}",
                "log_status": "Success",
                "log_by": request.session.get("user_data", {}).get("ID"),
            }]
            logparams = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1
            }
            # API call
            api_call(logparams, "prismMultipleinsert")

    except Exception as e:
        return HttpResponse(str(e), status=500)

    return redirect(f"/memberdetails/{request.POST.get("medicaid_id")}")

def add_member_alt_phone(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    try:
        if request.method == "POST":
            medicaid_id = request.POST.get("medicaid_id")
            phone_no = request.POST.get("alt_phone_no")

            # Data for alt phone table
            insertDataArray = [{
                "medicaid_id": medicaid_id,
                "alt_phone_no": phone_no,
                "add_by": request.session.get("user_data", {}).get("ID"),
            }]
            params = {
                "table_name": "MEM_ALT_PHONE",
                "insertDataArray": insertDataArray,
            }
            # API call
            api_call(params, "prismMultipleinsert")

            # Data for system log
            insertDataArray1 = [{
                "medicaid_id": medicaid_id,
                "action_type": f"Alt Phone changed {phone_no}",
                "log_name": "Alternative Phone",
                "log_details": f"Alternative Phone changed to {phone_no}",
                "log_status": "Success",
                "log_by": request.session.get("user_data", {}).get("ID"),
            }]
            logparams = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1,
            }
            # API call
            api_call(logparams, "prismMultipleinsert")

    except Exception as e:
        return HttpResponse(str(e), status=500)

    return redirect(f"/memberdetails/{request.POST.get("medicaid_id")}")


def add_member_alt_pnone(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    try:
        if request.method == "POST":
            medicaid_id = request.POST.get("medicaid_id")
            phone_no = request.POST.get("alt_phone_no")

            # ✅ Validate format: (123) 456-7890
            pattern = r'^\(\d{3}\) \d{3}-\d{4}$'
            if not re.match(pattern, phone_no or ""):
                return HttpResponse("Phone must be in format: (123) 456-7890", status=400)

            # Data for alt phone table
            insertDataArray = [{
                "medicaid_id": medicaid_id,
                "alt_phone_no": phone_no,
                "add_by": request.session.get("user_data", {}).get("ID"),
            }]
            params = {
                "table_name": "MEM_ALT_PHONE",
                "insertDataArray": insertDataArray,
            }
            # API call
            api_call(params, "prismMultipleinsert")

            # Data for system log
            insertDataArray1 = [{
                "medicaid_id": medicaid_id,
                "action_type": f"Alt Phone changed {phone_no}",
                "log_name": "Alternative Phone",
                "log_details": f"Alternative Phone changed to {phone_no}",
                "log_status": "Success",
                "log_by": request.session.get("user_data", {}).get("ID"),
            }]
            logparams = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1,
            }
            # API call
            api_call(logparams, "prismMultipleinsert")

    except Exception as e:
        return HttpResponse(str(e), status=500)

    return redirect(f"/memberdetails/{request.POST.get("medicaid_id")}")


def add_member_alt_language(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    try:
        if request.method == "POST":
            medicaid_id = request.POST.get("medicaid_id")
            code = request.POST.get("alt_language")
            alt_language = request.POST.get("alt_language_name")

            # Call API to get roster language + primary language
            param = {"medicaid_id": medicaid_id}
            response = api_call(param, "prismMemberlanguage")
            #print(response)
            roster_language = response["data"][0]["LANGUAGE_DESC"]
            language_code = response["data"][0]["PRIMARY_LANG"]

            # Insert into MEM_ALT_LANGUAGE
            insertDataArray = [{
                "medicaid_id": medicaid_id,
                "alt_language": alt_language,
                "code": code,
                "roster_language": roster_language,
                "language_code": language_code,
                "add_by": request.session.get("user_data", {}).get("ID"),
            }]
            langparams = {
                "table_name": "MEM_ALT_LANGUAGE",
                "insertDataArray": insertDataArray,
            }
            # API call
            api_call(langparams, "prismMultipleinsert")

            # Insert into MEM_SYSTEM_LOG
            insertDataArray1 = [{
                "medicaid_id": medicaid_id,
                "action_type": f"Alt Language changed {alt_language}",
                "log_name": "Alternative Language",
                "log_details": f"Alternative Language changed to {alt_language}",
                "log_status": "Success",
                "log_by": request.session.get("user_data", {}).get("ID"),
            }]
            logparams = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": insertDataArray1,
            }
            # API call
            api_call(logparams, "prismMultipleinsert")

    except Exception as e:
        return HttpResponse(str(e), status=500)

    return redirect(f"/memberdetails/{request.POST.get("medicaid_id")}")


def add_prisim_claim(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")
    try:
        if request.method == "POST":
            member_id = request.POST.get("member_id")
            claim_no = request.POST.get("txt_claim_number")
            dos = request.POST.get("date_dos")
            claim_type = request.POST.get("select_claim_type")
            physician = request.POST.get("txt_Physician")
            primary_diagnosis = request.POST.get("txt_primary_diagnosos")
            code_desc = request.POST.get("txt_code_desc")
            note = request.POST.get("textarea_claim_note")

            # Insert into MEM_SYSTEM_LOG
            insertDataArray = [{
                "DOCUMENT": claim_no,
                "FIRST_DOS":dos,
                "CLM_TYPE": claim_type,
                "PHYSICIAN": physician,
                "PRIMARY_DIAGNOSIS": primary_diagnosis,
                "CodeDesc": code_desc,
                "claim_note": note,
                "medicaid_id": member_id,
                "add_by": request.session.get("user_data", {}).get("ID"),
            }]
            params = {
                "table_name": "PRISM_CLAIM",
                "insertDataArray": insertDataArray,
            }
            # API call
            insert = api_call(params, "prismMultipleinsert")

    except Exception as e:
        return HttpResponse(str(e), status=500)

    return redirect(f"/memberdetails/{request.POST.get("member_id")}")


def add_rx_claim(request):
    if not request.session.get("is_logged_in", False):
        return redirect("login")

    if request.method == "POST":
        try:
            medicaid_id = request.POST.get("medicaid_id")
            rx_number = request.POST.get("rx_number")
            ndc = request.POST.get("ndc")
            drug_name = request.POST.get("drug_name")
            pharmacy = request.POST.get("pharmacy")
            service_date = request.POST.get("service_date")

            # 1. Rx Claim Data
            insertDataArray = [{
                "[Member ID]": medicaid_id,
                "[Rx number]": rx_number,
                "NDC": ndc,
                "[Drug name]": drug_name,
                "[Store Name]": pharmacy,
                "[Pharmacy NPI Num]": random.randint(100000, 999999999),
                "[Service Date]": service_date,
            }]

            params = {
                "table_name": "MERIDIAN_RX_CLAIMS",
                "insertDataArray": insertDataArray,
            }
            # API call
            insert = api_call(params, "prismMultipleinsert")

            # 2. If claim inserted, create alert
            if insert.get("statusCode") == 200:
                adata = [{
                    "medicaid_id": medicaid_id,
                    "alert_id": 64,
                    "alert_type": 65,
                    "alert_status": 1,
                    "alert_note": "Rx Alert",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "added_by": request.session.get("user_data", {}).get("ID"),
                    "source_type": "Rx",
                    "claim_number": rx_number,  # fixed from PHP bug (was Rxnumber)
                }]

                paramsalert = {
                    "table_name": "MEM_ALERTLIST",
                    "insertDataArray": adata,
                }
                api_call(paramsalert, "prismMultipleinsert")

                # 3. System Log
                all_log_row = {
                    "medicaid_id": medicaid_id,
                    "action_type": "Rx Alert",
                    "log_name": "Rx Alert",
                    "log_details": f"Rx Alert for {medicaid_id}",
                    "log_status": "Success",
                    "log_by": request.session.get("user_data", {}).get("ID"),
                }
                paramlog = {
                    "table_name": "MEM_SYSTEM_LOG",
                    "insertDataArray": [all_log_row],
                }
                api_call(paramlog, "prismMultipleinsert")

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")

        return redirect("memberdetails", medicaid_id=medicaid_id)


def update_member_indicator(request):
        if request.method == "POST":
            medicaid_id = request.POST.get("medicaid_id")
            # New updates
            high_drug_use = request.POST.get("HIGH_DRUG_USE")
            homeless = request.POST.get("HOMELESS")
            substance_abuse = request.POST.get("SUBSTANCE_ABUSE")

            updates = {
                "HIGH_DRUG_USE": high_drug_use,
                "HOMELESS": homeless,
                "SUBSTANCE_ABUSE": substance_abuse,
            }

            updatedata = {
                "updateData": updates,
                "table_name": "MEM_OUTREACH_MEMBERS",
                "id_field_name": "medicaid_id",
                "id_field_value": medicaid_id,
            }
            api_call(updatedata, "prismMultiplefieldupdate")

            all_log_row = {
                "medicaid_id": medicaid_id,
                "action_type": "Member indicator",
                "log_name": "Member indicator",
                "log_details": f"Member indicator flag updated successfully for {medicaid_id}",
                "log_status": "Success",
                "log_by": request.session.get("user_data", {}).get("ID"),
            }
            paramlog = {
                "table_name": "MEM_SYSTEM_LOG",
                "insertDataArray": [all_log_row],
            }
            api_call(paramlog, "prismMultipleinsert")

        return redirect("memberdetails", medicaid_id=request.POST.get("medicaid_id"))

def update_member_info(request):
    try:
        medicaid_id = request.POST.get("medicaid_id")
        preferred_call_time = request.POST.get("preferred_call_time")
        care_coordinator_id = request.POST.get("assign_to")

        # Prepare update data
        updata = {
            "preferred_call_time": preferred_call_time,
            "Care_Coordinator_id": care_coordinator_id,
        }

        dataList2 = {
            "updateData": updata,
            "table_name": "MEM_OUTREACH_MEMBERS",
            "id_field_name": "medicaid_id",
            "id_field_value": medicaid_id,
        }
        api_call(dataList2, "prismMultiplefieldupdate")

        all_log_row = {
            "medicaid_id": medicaid_id,
            "action_type": "Member update",
            "log_name": "Member info update",
            "log_details": f"Member info updated successfully for {medicaid_id}",
            "log_status": "Success",
            "log_by": request.session.get("user_data", {}).get("ID"),
        }
        paramlog = {
            "table_name": "MEM_SYSTEM_LOG",
            "insertDataArray": [all_log_row],
        }
        response = api_call(paramlog, "prismMultipleinsert")

        # Optional: check API response
        if response.get("statusCode") != 200:
            print("API Error:", response.text)

    except Exception as e:
        print("Error updating member info:", str(e))
        # You can also show a message or redirect to an error page

    return redirect("memberdetails", medicaid_id=request.POST.get("medicaid_id"))
def processmember(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    if request.method == "POST" and 'file' in request.FILES:
        session_id = str(uuid.uuid4())
        uploaded_file = request.FILES['file']

        decoded_file = uploaded_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)

        reader = csv.DictReader(io_string)

        # Map CSV headers → DB keys
        column_mapping = {
            "SUBSCRIBER_ID": "SUBSCRIBER_NUMBER",
            "FIRST_NM": "FIRST_NAME",
            "MIDDLE_NM": "MIDDLE_NAME",
            "LAST_NM": "LAST_NAME",
            "MEDICARE_ID": "MEDICARE_NO",
            "MEDICAID_ID": "RECIP_NO",
            "DT_OF_BIRTH": "BIRTH",
            "SEX": "SEX",
            "ADDRESS_1": "OTHER_ADDR1",
            "ADDRESS_2": "OTHER_ADDR2",
            "CITY": "OTHER_CITY",
            "STATE": "OTHER_STATE",
            "ZIP_CODE": "OTHER_ZIP",
            "HOME_TELEPHONE": "OTHER_PHONE",
            "ENROLL_DT": "EFFCT_DT",
            "DISENROLL_DT": "PROP_DISENROLL_DATE",
            "DISENROLL_RSN_CD": "PROP_DISENR_RSN"
        }

        data = []
        total_inserted_members = 0
        #processSuccessMsg = ""
        for row in reader:
            filtered_row = {
                new_key: row.get(old_key, "")
                for old_key, new_key in column_mapping.items()
            }
            data.append(filtered_row)

        insertDataArray = []
        insertOutreachArray = []

        for idx, row in enumerate(data):
            # --- Members table row ---
            member_row = {
                "SUBSCRIBER_NUMBER": row["SUBSCRIBER_NUMBER"],
                "FIRST_NAME": row["FIRST_NAME"],
                "MIDDLE_NAME": row["MIDDLE_NAME"],
                "LAST_NAME": row["LAST_NAME"],
                "MEDICARE_NO": row["MEDICARE_NO"],
                "RECIP_NO": row["RECIP_NO"],
                "MEM_NO": row["RECIP_NO"],
                "BIRTH": clean_date(row["BIRTH"]),
                "SEX": row["SEX"],
                "OTHER_ADDR1": row["OTHER_ADDR1"],
                "OTHER_ADDR2": row["OTHER_ADDR2"],
                "OTHER_CITY": row["OTHER_CITY"],
                "OTHER_STATE": row["OTHER_STATE"],
                "OTHER_ZIP": row["OTHER_ZIP"],
                "OTHER_PHONE": row["OTHER_PHONE"],
                "EFFCT_DT": clean_date(row["EFFCT_DT"]),
                "PROP_DISENR_RSN": row["PROP_DISENR_RSN"],
                "INSERT_SESSION_ID": session_id
            }
            insertDataArray.append(member_row)

            # --- Outreach members row ---
            care_coordinator_id = 1 if idx % 2 == 0 else 2
            outreach_row = {
                "medicaid_id": row["RECIP_NO"],
                "mem_type": "OUTREACH",
                "current_session": session_id,
                "Care_Coordinator_id": care_coordinator_id,
                "language": "01",
                "zipcode": row["OTHER_ZIP"]
            }
            insertOutreachArray.append(outreach_row)

        # --- Helper to split into batches of 1000 ---
        def chunked(iterable, size=1000):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]

        # --- Insert Members ---
        for batch_num, batch in enumerate(chunked(insertDataArray, 1000), start=1):
            print(f"Processing MEM_MEMBERS batch {batch_num}, rows: {len(batch)}")
            apidata = {
                "table_name": "MEM_MEMBERS",
                "insertDataArray": batch,
            }
            insertresult = api_call(apidata, "prismMultipleinsert")

        # --- Insert Outreach Members ---
        for batch_num, batch in enumerate(chunked(insertOutreachArray, 1000), start=1):
            print(f"Processing MEM_OUTREACH_MEMBERS batch {batch_num}, rows: {len(batch)}")
            apidata = {
                "table_name": "MEM_OUTREACH_MEMBERS",
                "insertDataArray": batch,
            }
            insertresult = api_call(apidata, "prismMultipleinsert")
            # If API succeeded → count these rows
            if insertresult.get("statusCode") == 200:
                total_inserted_members += len(batch)
        messages.success(
            request,
            f"{total_inserted_members} members processed successfully."
        )
    return render(request, 'processmember.html', {
        'pageTitle': "PROCESS MEMBER",
        'projectName': settings.PROJECT_NAME,
    })
def processriskgap(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')
    data = []
    total_inserted_gaps = 0
    if request.method == "POST":
        if 'file' in request.FILES:
            session_id = str(uuid.uuid4())  # same for this file upload
            uploaded_file = request.FILES['file']

            decoded_file = uploaded_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)

            reader = csv.DictReader(io_string)

            # Map CSV headers → desired keys
            column_mapping = {
                "PAT_ID": "PAT_ID",
                "MBR_ID": "SUBSCRIBER_NUMBER",
                "PRODUCT_TYPE": "PRODUCT_TYPE",
                "HCC_CATEGORY": "HCC_CATEGORY",
                "HCC_MODEL": "HCC_MODEL",
                "STATUS": "STATUS",
                "RELEVANT_DATE": "RELEVANT_DATE",
                "DIAG_SOURCE": "DIAG_SOURCE",
                "DIAG_CODE": "DIAG_CODE",
                "DIAG_DESC": "DIAG_DESC",
                "PROV_SPECIALTY": "PROV_SPECIALTY"
            }

            # Extract only mapped columns
            for row in reader:
                filtered_row = {
                    new_key: row.get(old_key, "")
                    for old_key, new_key in column_mapping.items()
                }
                data.append(filtered_row)

            insertDataArray = []
            for row in data:
                member_row = {
                    "PAT_ID": row["PAT_ID"],
                    "SUBSCRIBER_NUMBER": row["SUBSCRIBER_NUMBER"],
                    "PRODUCT_TYPE": row["PRODUCT_TYPE"],
                    "HCC_CATEGORY": row["HCC_CATEGORY"],
                    "HCC_MODEL": row["HCC_MODEL"],
                    "STATUS": row["STATUS"],
                    "RELEVANT_DATE": clean_date(row["RELEVANT_DATE"]),
                    "DIAG_SOURCE": row["DIAG_SOURCE"],
                    "DIAG_CODE": row["DIAG_CODE"],
                    "DIAG_DESC": escape_sql_string(row["DIAG_DESC"]),
                    "PROV_SPECIALTY": row["PROV_SPECIALTY"],
                    "INSERT_SESSION_ID": session_id
                }
                insertDataArray.append(member_row)
            #insertDataArray = insertDataArray[:500]
            # --- Split into batches of 1000 rows ---
            def chunked(iterable, size=1000):
                for i in range(0, len(iterable), size):
                    yield iterable[i:i + size]

            # Send batches
            batch_num = 0
            for batch in chunked(insertDataArray, 1000):
                batch_num += 1
                print(f"Processing batch {batch_num}, rows: {len(batch)}")

                apidata = {
                    "table_name": "MEM_RISK_GAP",
                    "insertDataArray": batch,
                }
                insertresult = api_call(apidata, "prismMultipleinsert")
                print("Renamed Data:", insertresult)
                # If API succeeded → count these rows
                if insertresult.get("statusCode") == 200:
                    total_inserted_gaps += len(batch)
            messages.success(
                request,
                f"{total_inserted_gaps} risk gaps processed successfully."
            )
            #print("Renamed Data:", insertDataArray[:5])
    return render(request, 'processriskgap.html', {
        'pageTitle': "PROCESS RISK GAP",
        'projectName': settings.PROJECT_NAME,

    })
def escape_sql_string(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.replace("'", "''")
    return value
def clean_date(value):
    if not value or value.strip().upper() in ["NULL", "NONE", ""]:
        return None  # send NULL instead of string

    possible_formats = [
        "%Y-%m-%d",   # 1979-01-01
        "%m/%d/%Y",   # 01/01/1979
        "%m/%d/%y",   # 01/01/79
        "%d-%m-%Y",   # 01-01-1979
    ]

    for fmt in possible_formats:
        try:
            dt = datetime.strptime(value.strip(), fmt)
            # Ensure within smalldatetime range
            if 1900 <= dt.year <= 2079:
                return dt.strftime("%Y-%m-%d")
            return None
        except ValueError:
            continue

    return None


def star_performance(request):
    return render(request, 'star_performance.html', {
        'pageTitle': "STAR PERFORMANCE",
        'projectName': settings.PROJECT_NAME,
    })
def processquality(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')
    data = []
    total_inserted_gaps = 0
    if request.method == "POST":
        if 'file' in request.FILES:
            session_id = str(uuid.uuid4())  # same for this file upload
            uploaded_file = request.FILES['file']

            decoded_file = uploaded_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)

            reader = csv.DictReader(io_string)

            # Map CSV headers → desired keys
            column_mapping = {
                "Subscriber ID": "SUBSCRIBER_ID",
                "Measure Name": "MEASURE_NAME",
                "Submeasure": "SUB_MEASURE",
                "First Name": "FIRST_NAME",
                "Middle Name": "MIDDLE_NAME",
                "Last Name": "LAST_NAME",
                "Medicare ID": "MEDICARE_ID",
                "Medicaid ID": "MEDICAID_ID",
                "Date of Birth": "DOB",
                "Sex": "SEX",
                "Provider ID": "PROVIDER_ID",
                "Provider Name": "PROVIDER_NAME",
                "Numerator_Gap": "NUMERATOR_GAP"
            }

            # Extract only mapped columns
            for row in reader:
                filtered_row = {
                    new_key: row.get(old_key, "")
                    for old_key, new_key in column_mapping.items()
                }
                data.append(filtered_row)

            insertDataArray = []
            for row in data:
                member_row = {
                    "SUBSCRIBER_ID": row["SUBSCRIBER_ID"],
                    "MEASURE_NAME": row["MEASURE_NAME"],
                    "SUB_MEASURE": row["SUB_MEASURE"],
                    "FIRST_NAME": row["FIRST_NAME"],
                    "MIDDLE_NAME": row["MIDDLE_NAME"],
                    "LAST_NAME": row["LAST_NAME"],
                    "MEDICARE_ID": row["MEDICARE_ID"],
                    "MEDICAID_ID": row["MEDICAID_ID"],
                    "DOB": escape_sql_string(row["DOB"]),
                    "SEX": row["SEX"],
                    "PROVIDER_ID": row["PROVIDER_ID"],
                    "PROVIDER_NAME": row["PROVIDER_NAME"],
                    "NUMERATOR_GAP": row["NUMERATOR_GAP"],
                    "INSERT_SESSION_ID": session_id
                }
                insertDataArray.append(member_row)
            #insertDataArray = insertDataArray[:500]
            #print(insertDataArray)
            # --- Split into batches of 1000 rows ---
            def chunked(iterable, size=1000):
                for i in range(0, len(iterable), size):
                    yield iterable[i:i + size]

            # Send batches
            batch_num = 0
            for batch in chunked(insertDataArray, 1000):
                batch_num += 1
                print(f"Processing batch {batch_num}, rows: {len(batch)}")

                apidata = {
                    "table_name": "MEM_CIH_QUALITY",
                    "insertDataArray": batch,
                }
                insertresult = api_call(apidata, "prismMultipleinsert")
                print("Renamed Data:", insertresult)
                # If API succeeded → count these rows
                if insertresult.get("statusCode") == 200:
                    total_inserted_gaps += len(batch)
            messages.success(
                request,
                f"{total_inserted_gaps} CIH Quality processed successfully."
            )
            #print("Renamed Data:", insertDataArray[:5])
    return render(request, 'processquality.html', {
        'pageTitle': "PROCESS QUALITY",
        'projectName': settings.PROJECT_NAME,
    })
