# outreach/api.py
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Example dummy data (later replace with DB query)
ACTION_RESULTS = [
    {"id": 1, "action_result": "Pending"},
    {"id": 2, "action_result": "Completed"},
    {"id": 3, "action_result": "Failed"},
]

def api_call(params, funName):
    api_url = settings.API_URL + funName
    response = requests.post(api_url, json=params)
    return response.json()

@csrf_exempt
def get_scheduled_action_status(request):
    if request.method == "POST":
        scheduled_type = request.POST.get("scheduled_type")
        params = {"scheduled_type": scheduled_type}
        resultfollowupResponse = api_call(params, "prismActionresultfollowup")
        return JsonResponse(resultfollowupResponse['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_vendor_list(request):
    if request.method == "POST":
        vendor_name = request.POST.get("vendor_name")
        params = {"vendor_name": vendor_name}
        vendorApi = api_call(params, "prismVendorlist")
        return JsonResponse(vendorApi['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_doctor_list(request):
    if request.method == "POST":
        doctor_name = request.POST.get("doctor_name")
        vendor_id = request.POST.get("vendor_id")
        params = {"vendor_id": vendor_id,"doctor_name": doctor_name}
        vendorApi = api_call(params, "prismProviderlist")
        return JsonResponse(vendorApi['data'], safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)
@csrf_exempt
def get_call_history(request):
    if request.method == "POST":
        medicaid_id = request.POST.get("medicaid_id")
        params = {"medicaid_id": medicaid_id}
        resultcallHistoryResponse = api_call(params, "prismGetcallhistory")
        return JsonResponse(resultcallHistoryResponse, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)
