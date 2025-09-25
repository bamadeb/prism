# outreach/api.py
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def api_call(params, funName):
    api_url = settings.API_URL + funName
    response = requests.post(api_url, json=params)
    return response.json()

@csrf_exempt
def get_scheduled_action_status(request):
    if request.method == "POST":
        scheduled_type = request.POST.get("scheduled_type")
        params = {"scheduled_type": scheduled_type}
        resultfollowupResponse = api_call(params, "prismActionresultfollowup"+"-"+settings.ENVIRONMENT)
        return JsonResponse(resultfollowupResponse['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_vendor_list(request):
    if request.method == "POST":
        vendor_name = request.POST.get("vendor_name")
        params = {"vendor_name": vendor_name}
        vendorApi = api_call(params, "prismVendorlist"+"-"+settings.ENVIRONMENT)
        return JsonResponse(vendorApi['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_doctor_list(request):
    if request.method == "POST":
        doctor_name = request.POST.get("doctor_name")
        vendor_id = request.POST.get("vendor_id")
        params = {"vendor_id": vendor_id,"doctor_name": doctor_name}
        vendorApi = api_call(params, "prismProviderlist"+"-"+settings.ENVIRONMENT)
        return JsonResponse(vendorApi['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)
@csrf_exempt
def get_call_history(request):
    if request.method == "POST":
        medicaid_id = request.POST.get("medicaid_id")
        params = {"medicaid_id": medicaid_id}
        resultcallHistoryResponse = api_call(params, "prismGetcallhistory"+"-"+settings.ENVIRONMENT)
        return JsonResponse(resultcallHistoryResponse, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_gap_list(request):
    if request.method == "POST":
        medicaid_id = request.POST.get("medicaid_id")
        params = {"medicaid_id": medicaid_id}
        resultcallHistoryResponse = api_call(params, "prismGetgapList"+"-"+settings.ENVIRONMENT)
        return JsonResponse(resultcallHistoryResponse, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)
@csrf_exempt
def get_quality_list(request):
    if request.method == "POST":
        medicaid_id = request.POST.get("medicaid_id")
        params = {"medicaid_id": medicaid_id}
        resultcallHistoryResponse = api_call(params, "prismGetqualityList"+"-"+settings.ENVIRONMENT)
        return JsonResponse(resultcallHistoryResponse, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_alert_typeList(request):
    if request.method == "POST":
        alert_id = request.POST.get("alert_id")
        params = {"alert_id": alert_id}
        response = api_call(params, "prismAlertTypeListbyAlertId"+"-"+settings.ENVIRONMENT)
        return JsonResponse(response['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_user_details(request):
    if request.method == "POST":
        id = request.POST.get("id")
        params = {"user_id": id}
        response = api_call(params, "prismUserListByRole"+"-"+settings.ENVIRONMENT)
        return JsonResponse(response['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)


