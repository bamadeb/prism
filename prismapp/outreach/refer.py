import random
import requests ,json,re
import urllib3,os,secrets,string
from django.conf import settings

from django.http import HttpResponse
from django.shortcuts import redirect

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def api_call(params, funName):
    api_url = settings.API_URL + funName +"-"+settings.ENVIRONMENT
    response = requests.post(api_url, json=params)
    return response.json()

def add_referral(request):
    if request.method == "POST":
        #print(request.POST)
        #return HttpResponse("Not allowed")

        ref_medicaid_id = request.POST.get('ref_medicaid_id', '')
        department_id = request.POST.get('department_id', '')
        referring_reason = request.POST.get('referring_reason', '')
        referral_to = request.POST.get('referral_user_id', '')

        user_data = request.session.get('user_data', {})
        referral_by = user_data.get('ID')

        # Split medicaid IDs into list
        medicaid_ids = ref_medicaid_id.split(',') if ref_medicaid_id else []

        insertDataArray = []
        loginsertDataArray = []

        for medicaid_id in medicaid_ids:
            medicaid_id = medicaid_id.strip()  # Clean any whitespace

            # Referral insert data
            insert_data = {
                "medicaid_id": medicaid_id,
                "department_id": department_id,
                "referring_reason": referring_reason,
                "refer_to": referral_to,
                "refer_by": referral_by
            }
            insertDataArray.append(insert_data)

            # System log insert data
            loginsert_data = {
                "medicaid_id": medicaid_id,
                "log_name": 'MEMBER REFERRAL',
                "log_details": f'MEMBER REFERRAL TO {referral_to}',
                "log_status": 'Success',
                "log_by": referral_by,
                "action_type": 'REFERRAL',
            }
            loginsertDataArray.append(loginsert_data)

            # Update Care Coordinator
            update_data = {
                "Care_Coordinator_id": referral_to
            }
            update_payload = {
                "updateData": update_data,
                "table_name": "MEM_OUTREACH_MEMBERS",
                "id_field_name": "medicaid_id",
                "id_field_value": medicaid_id,
            }
            api_call(update_payload, "prismMultiplefieldupdate")

        # Insert referrals
        referral_payload = {
            "table_name": "MEM_REFERRING",
            "insertDataArray": insertDataArray,
        }
        api_call(referral_payload, "prismMultipleinsert")

        # Insert logs
        log_payload = {
            "table_name": "MEM_SYSTEM_LOG",
            "insertDataArray": loginsertDataArray,
        }
        api_call(log_payload, "prismMultipleinsert")

    return redirect("mywork")

