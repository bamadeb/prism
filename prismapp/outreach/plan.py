import random
import requests ,json,re
import urllib3,os,secrets,string
from django.conf import settings
from django.contrib import messages

from django.http import HttpResponse
from django.shortcuts import redirect, render

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def api_call(params, funName):
    api_url = settings.API_URL + funName +"-"+settings.ENVIRONMENT
    response = requests.post(api_url, json=params)
    return response.json()

def assign_plan(request):
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
            #print(plan_exist)
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
        print(insertDataArray)
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


def plans(request):
    if not request.session.get('is_logged_in', False):  # Check session value
        return render(request, 'login.html')
    else:
        params = {}
        plan_list = api_call(params, "prsmPlandetails")
        #print(plan_list)
        context = {
            'pageTitle': "PLANS LIST",
            'projectName': settings.PROJECT_NAME,
            "planlist": plan_list['data']['planlist'],
            "plandetailslist": plan_list['data']['plandetailslist'],
        }
    return render(request, 'plans.html', context)

def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)  # ensure dir exists

    upload_path = os.path.join(upload_dir, f.name)
    with open(upload_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    #print(f"File saved to: {upload_path}")

def add_plan(request):
    if request.method != "POST":
        return HttpResponse("Not allowed", status=405)

    user_data = request.session.get('user_data', {})
    added_by = user_data.get('ID')

    plan_id = int(request.POST.get('plan_id', 0))
    edit_plan_id = request.POST.get('edit_plan_id')
    plan_document_id = request.POST.get('plan_document_id')
    status = request.POST.get('status')

    uploaded_file = request.FILES.get('file_name')
    file_name = uploaded_file.name if uploaded_file else None
    file_extension = os.path.splitext(file_name)[1] if file_name else None

    def insert_plan(plan_data):
        payload = {
            "table_name": "MEM_PLAN_MASTER",
            "insertDataArray": [plan_data],
        }
        return api_call(payload, "prismMultipleinsert")

    def update_plan(plan_id, data):
        payload = {
            "updateData": data,
            "table_name": "MEM_PLAN_MASTER",
            "id_field_name": "id",
            "id_field_value": plan_id,
        }
        return api_call(payload, "prismMultiplefieldupdate")

    def insert_plan_document(plan_id):
        """Insert file metadata into MEM_PLAN_DOCUMENTS"""
        if not uploaded_file:
            return
        handle_uploaded_file(uploaded_file)
        file_data = {
            "plan_id": plan_id,
            "file_name": file_name,
            "file_type": file_extension,
            "added_by": added_by,
            "status": status
        }
        payload = {
            "table_name": "MEM_PLAN_DOCUMENTS",
            "insertDataArray": [file_data],
        }
        api_call(payload, "prismMultipleinsert")

    def update_plan_document(doc_id):
        """Update document info if edit mode"""
        if uploaded_file:
            handle_uploaded_file(uploaded_file)
            update_data = {
                "file_name": file_name,
                "file_type": file_extension,
                "status": status
            }
        else:
            update_data = {
                "status": status
            }
        payload = {
            "updateData": update_data,
            "table_name": "MEM_PLAN_DOCUMENTS",
            "id_field_name": "id",
            "id_field_value": doc_id,
        }
        api_call(payload, "prismMultiplefieldupdate")

    # ---------- MAIN LOGIC ----------

    # CASE 1: Edit existing plan
    if edit_plan_id:
        update_data = {
            "plan_name": request.POST.get("plan_name"),
            "start_date": request.POST.get("start_date"),
            "end_date": request.POST.get("end_date")
        }
        update_plan(edit_plan_id, update_data)
        update_plan_document(plan_document_id)

    # CASE 2: Add new plan
    elif plan_id == 0:
        plan_data = {
            "plan_name": request.POST.get("plan_name"),
            "start_date": request.POST.get("start_date"),
            "end_date": request.POST.get("end_date"),
        }
        insert_result = insert_plan(plan_data)

        inserted_id = insert_result.get("insertedIds")
        # handle case where API returns a list like [13]
        if isinstance(inserted_id, list) and len(inserted_id) == 1:
            inserted_id = inserted_id[0]

        if inserted_id:
            insert_plan_document(inserted_id)

    # CASE 3: Existing plan (no edit), new document upload
    else:
        insert_plan_document(plan_id)

    return redirect("plans")
