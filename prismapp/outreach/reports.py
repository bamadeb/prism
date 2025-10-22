import calendar,requests
from datetime import date
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect

def api_call(params, funName):
    api_url = settings.API_URL + funName +"-"+settings.ENVIRONMENT
    response = requests.post(api_url, json=params)
    return response.json()

def gapsreport(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    today = date.today()
    startdate = today.replace(day=1)
    enddate = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    if request.POST.get("start_date"):
        start_date = request.POST.get("start_date")
    else:
        start_date = startdate.strftime("%m/%d/%Y")

    if request.POST.get("end_date"):
        end_date = request.POST.get("end_date")
    else:
        end_date = enddate.strftime("%m/%d/%Y")

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }
    gap_observation = api_call(params, "prismGetgapsobservationdata")

    #print(gap_observation['data'])

    return render(request, 'gapsreport.html', {
        'pageTitle': "GAPS REPORT",
        "start_date": start_date,
        "end_date": end_date,
        "user_list": gap_observation['data'],
    })