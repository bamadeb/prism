import calendar,requests
import csv
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
        'pageTitle': "RISK GAPS REPORT",
        "start_date": start_date,
        "end_date": end_date,
        "user_list": gap_observation['data'],
    })

def risk_profile(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    # ---- Initialize data structures ----
    category_array = {}
    member_total_risk = {}
    risk_grouped = {}
    toDateArray = []
    flat_category_array = {}
    flat_for_template = []  # ✅ Added flattened version

    # ---- Prepare API parameters ----
    params = {}
    if request.POST.get("user_id"):
        params["user_id"] = request.POST.get("user_id")

    # ---- API data ----
    member_details_monthly_score = api_call(params, "prismMemberriskprofile")
    monthly_score_data = member_details_monthly_score["data"]["riskSummary"]
    user_list = member_details_monthly_score["data"]["userlist"]

    # ---- Build structured data ----
    for row in monthly_score_data:
        care_user = row.get("Care_Coordinator_name", "UNKNOWN")
        member = row.get("member_name", "UNKNOWN")
        medicaid_id = row.get("medicaid_id")
        category = row.get("risk_category")
        subcat = row.get("sub_category_name")
        specific = row.get("sub_category2_name")
        date_str = row.get("to_date", "")
        score = row.get("score", 0)
        level = row.get("level", "N/A")

        # ---- Date clean ----
        date_clean = date_str.split("T")[0] if "T" in date_str else date_str
        if date_clean not in toDateArray:
            toDateArray.append(date_clean)

        # ---- Member total by month ----
        member_total_risk.setdefault(care_user, {})
        member_total_risk[care_user].setdefault(medicaid_id, {})
        member_total_risk[care_user][medicaid_id].setdefault(date_clean, 0)
        member_total_risk[care_user][medicaid_id][date_clean] += score

        # ---- Build nested category data ----
        category_array.setdefault(care_user, {})
        category_array[care_user].setdefault(medicaid_id, {})
        category_array[care_user][medicaid_id].setdefault(category, {})
        category_array[care_user][medicaid_id][category].setdefault(subcat, {})
        category_array[care_user][medicaid_id][category][subcat].setdefault(specific, {})

        category_array[care_user][medicaid_id][category][subcat][specific][date_clean] = {
            "score": score,
            "level": level,
        }

    # ---- Sort dates chronologically ----
    toDateArray = sorted(set(toDateArray), key=lambda d: datetime.strptime(d, "%m-%Y"))
    last_date = toDateArray[-1] if toDateArray else None

    # ---- Flatten data for easy template iteration ----
    for care_user, member_dict in category_array.items():
        for medicaid_id, cat_dict in member_dict.items():
            flat_category_array.setdefault(care_user, {})
            flat_category_array[care_user].setdefault(medicaid_id, [])

            for category, subcats in cat_dict.items():
                for subcat, specifics in subcats.items():
                    for specific, scores in specifics.items():
                        score_list = [
                            {
                                "date": d,
                                "score": v.get("score", "-"),
                                "level": v.get("level", "N/A")
                            }
                            for d, v in scores.items()
                        ]
                        flat_category_array[care_user][medicaid_id].append({
                            "category": category,
                            "sub_category": subcat,
                            "specific": specific,
                            "scores_list": score_list,
                        })
                        # ✅ Add flattened entry
                        flat_for_template.append({
                            "user": care_user,
                            "member_id": medicaid_id,
                            "items": [{
                                "category": category,
                                "sub_category": subcat,
                                "specific": specific,
                                "scores_list": score_list,
                            }],
                        })

    # ---- Determine risk levels (per user) ----
    for user, members in member_total_risk.items():
        risk_grouped.setdefault(user, {
            "RISK LEVEL-1": {},
            "RISK LEVEL-2": {},
            "RISK LEVEL-3": {}
        })

        for member_id, scores in members.items():
            total = scores.get(last_date, 0)
            if total < 3:
                level = "RISK LEVEL-1"
            elif 3 <= total <= 7:
                level = "RISK LEVEL-2"
            else:
                level = "RISK LEVEL-3"

            risk_grouped[user][level][member_id] = total

    # ---- Render ----
    return render(request, "risk_profile.html", {
        "pageTitle": "MEMBER RISK PROFILE",
        "user_list": user_list,
        "toDateArray": toDateArray,
        "category_array": category_array,
        "member_total_risk": member_total_risk,
        "risk_grouped": risk_grouped,
        "user_id": request.POST.get("user_id"),
        "last_date": last_date,
        "flat_for_template": flat_for_template,  # ✅ New key
        "colspan_count": len(toDateArray) + 10,   # ✅ for colspan in template
    })

def download_users_csv(request):
    today = date.today()
    startdate = today.replace(day=1)
    enddate = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    # Read dates from GET parameters or use defaults
    start_date = request.GET.get("start_date", startdate.strftime("%m/%d/%Y"))
    end_date = request.GET.get("end_date", enddate.strftime("%m/%d/%Y"))

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    # Call your API
    gap_observation = api_call(params, "prismGetgapsobservationdata")

    # Define header
    header = [
        'MEMBER ID','PATIENT MEMBER ID','PATIENT CMS MEDICARE NUMBER','MEMBER FIRST NAME','MEMBER LAST NAME','MEMBER DOB', 'OBSERVATION DATE', 'OBSERVATION YEAR', 'OBSERVATION CODE', 'CPT CODE MODIFIER',
        'OBSERVATION CODE SET', 'OBSERVATION RESULT', 'SERVICE PROVIDER NPI', 'SERVICE PROVIDER TAXONOMY CODE',
        'SERVICE PROVIDER NAME', 'SERVICE PROVIDER TYPE', 'SERVICE PROVIDER RXPROVIDERFLAG', 'PROVIDER GROUP NPI',
        'PROVIDER GROUP TAXONOMY CODE', 'PROVIDER GROUP NAME', 'SOURCE'
    ]

    # Prepare body data
    body = []
    for obs_data in gap_observation.get('data', []):
        if obs_data.get('ObservationDate') == "01/01/1900":
            obs_data['ObservationDate'] = ""

        body.append([
            obs_data.get('RECIP_NO', ''),
            obs_data.get('RECIP_NO', ''),
            obs_data.get('MEDICARE_NO', ''),
            obs_data.get('FIRST_NAME', ''),
            obs_data.get('LAST_NAME', ''),
            obs_data.get('BIRTH', ''),
            obs_data.get('ObservationDate', ''),
            obs_data.get('Observation_Year', ''),
            obs_data.get('Observation_Code', ''),
            obs_data.get('CPT_Code_Modifier', ''),
            obs_data.get('Observation_Code_Set', ''),
            obs_data.get('Observation_Result', ''),
            obs_data.get('Service_Provider_NPI', ''),
            obs_data.get('Service_Provider_Taxonomy_Code', ''),
            obs_data.get('Service_Provider_Name', ''),
            obs_data.get('Service_Provider_Type', ''),
            obs_data.get('Service_Provider_RxProviderFlag', ''),
            obs_data.get('Provider_Group_NPI', ''),
            obs_data.get('Provider_Group_Taxonomy_Code', ''),
            obs_data.get('Provider_Group_Name', ''),
            obs_data.get('Source', '')
        ])

    # Create HTTP response with CSV data
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="risk_gaps_observation_data.csv"'

    writer = csv.writer(response)
    writer.writerow(header)   # Write headers first
    writer.writerows(body)    # Then write all data rows

    return response