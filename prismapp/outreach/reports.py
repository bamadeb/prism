import calendar,requests
from collections import defaultdict
from datetime import date
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from datetime import datetime

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

def risk_profile(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    memberTotalRiskArray = {}
    category_array = {}
    categorywise_sort_array = {}
    toDateArray = []
    to_date_array = []
    farray = []

    if request.POST.get("user_id"):
        params = {
            "user_id": request.POST.get("user_id")
        }
    else:
        params = {}

    member_details_monthly_score = api_call(params, "prismMemberriskprofile")
    monthly_score_data = member_details_monthly_score['data']['riskSummary']
    #print(monthly_score_data)
    t_date = ''

    for key, monthly_score in enumerate(monthly_score_data):
        level = monthly_score.get('level')
        if level:
            care_coordinator = monthly_score['Care_Coordinator_name']
            member_name = monthly_score['member_name']
            subcat2_name = monthly_score['sub_category2_name']

            # Initialize nested dicts as needed
            category_array.setdefault(care_coordinator, {})
            category_array[care_coordinator].setdefault(member_name, {})
            category_array[care_coordinator][member_name].setdefault(subcat2_name, {'data': {}})

            # --- Total risk by member ---
            memberTotalRiskArray.setdefault(member_name, {})  # ensure the member exists
            memberTotalRiskArray[member_name].setdefault(monthly_score['to_date'], 0)  # ensure the date exists

            # Now you can safely add
            memberTotalRiskArray[member_name][monthly_score['to_date']] += monthly_score['score']

            print(memberTotalRiskArray[member_name])
            # --- Assign values ---
            data_dict = category_array[care_coordinator][member_name][subcat2_name]['data']
            data_dict[key] = {
                'to_date': monthly_score['to_date'],
                'score': monthly_score['score'],
                'level': monthly_score['level'],
            }

            t_date = monthly_score['to_date']

            # --- Assign sort value based on level ---
            if level == 'High':
                sort_value = 3
            elif level == 'Medium':
                sort_value = 2
            elif level == 'Low':
                sort_value = 1
            else:
                sort_value = 0  # default/fallback

            data_dict[key]['sort'] = sort_value

            # --- Copy static fields at this level ---
            category_array[care_coordinator][member_name][subcat2_name]['sub_category2_id'] = monthly_score[
                'sub_category2_id']
            category_array[care_coordinator][member_name][subcat2_name]['risk_category'] = monthly_score[
                'risk_category']
            category_array[care_coordinator][member_name][subcat2_name]['sub_category_name'] = monthly_score[
                'sub_category_name']

            # --- Update sort array ---
            categorywise_sort_array.setdefault(care_coordinator, {})
            categorywise_sort_array[care_coordinator].setdefault(member_name, {})
            categorywise_sort_array[care_coordinator][member_name][subcat2_name] = sort_value

            # --- Append formatted date ---
            date_str = monthly_score['to_date'].split('T')[0]  # gets '2025-10-24'
            toDateArray.append(date_str)

        data = {}
        to_date_array = sorted(set(toDateArray), key=lambda x: datetime.strptime("01-" + x, "%d-%m-%Y"))
        sorted_categorywise = dict(
            sorted(categorywise_sort_array.items(), key=lambda item: item[1].get('score', 0), reverse=True)
        )
        last_date = to_date_array[-1]

        newarray = {}
        for key, categorywise in sorted_categorywise.items():
            onelinearray = category_array[key]
            inner_dict = list(onelinearray.values())[0]
            sub_category_dict = list(inner_dict.values())[0]
            risk_category = sub_category_dict['risk_category']
            newarray.setdefault(risk_category, {})[key] = onelinearray


        farray = {}
        for key, mainarray111 in newarray.items():
            farray = mainarray111

    return render(request, 'risk_profile.html', {
        'pageTitle': "MEMBER RISK PROFILE",
        'user_list': member_details_monthly_score['data']['userlist'],
        'toDateArray': to_date_array,
        'tabarray': farray,
        'member_total_risk_array': memberTotalRiskArray,
        'user_id': request.POST.get("user_id"),
        'last_date': last_date,
    })