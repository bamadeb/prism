import random
import requests ,json,re
import urllib3,os,secrets,string
from django.conf import settings
from django.contrib import messages

from django.http import HttpResponse
from django.shortcuts import redirect

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def api_call(params, funName):
    api_url = settings.API_URL + funName +"-"+settings.ENVIRONMENT
    response = requests.post(api_url, json=params)
    return response.json()

def add_plan(request):
    if request.method == "POST":
        #print(request.POST)
        #return HttpResponse("Not allowed")

        plan_medicaid_id = request.POST.get('plan_medicaid_id', '')
        plan_id = request.POST.get('plan_id', '')

        user_data = request.session.get('user_data', {})
        referral_by = user_data.get('ID')


        # Split medicaid IDs into list
        medicaid_ids = plan_medicaid_id.split(',') if plan_medicaid_id else []

        for medicaid_id in medicaid_ids:
            medicaid_id = medicaid_id.strip()
            params = {
                "medicaid_id": medicaid_id,
                "plan_id": plan_id
            }
            plan_exist = api_call(params, "prismPlanexist")
            print(plan_exist)
            if plan_exist.get('data') and len(plan_exist['data']) > 0:
                messages.error(request, "Plan already exists for member: #"+ medicaid_id)
                return redirect('mywork')


        insertDataArray = []
        loginsertDataArray = []

        for medicaid_id in medicaid_ids:
            medicaid_id = medicaid_id.strip()  # Clean any whitespace

            # Referral insert data
            insert_data = {
                "plan_id": plan_id,
                "medicaid_id": medicaid_id,
                "added_by": referral_by
            }
            insertDataArray.append(insert_data)

            # System log insert data
            loginsert_data = {
                "medicaid_id": medicaid_id,
                "log_name": 'ASSIGN PLAN',
                "log_details": f'ASSIGN PLAN TO {medicaid_id}',
                "log_status": 'Success',
                "log_by": referral_by,
                "action_type": 'ASSIGN PLAN',
            }
            loginsertDataArray.append(loginsert_data)

        # Insert referrals
        plan_payload = {
            "table_name": "MEM_PLAN_MEMBERS",
            "insertDataArray": insertDataArray,
        }
        api_call(plan_payload, "prismMultipleinsert")

        # Insert logs
        log_payload = {
            "table_name": "MEM_SYSTEM_LOG",
            "insertDataArray": loginsertDataArray,
        }
        api_call(log_payload, "prismMultipleinsert")

    return redirect("mywork")

