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
    # ---- Check session ----
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    # ---- Initialize data structures ----
    category_array = {}
    member_total_risk = {}
    risk_grouped = {}
    toDateArray = []
    flat_category_array = {}
    flat_for_template = []

    # ---- Prepare API parameters ----
    params = {}
    if request.POST.get("user_id"):
        params["user_id"] = request.POST.get("user_id")

    # ---- Fetch API Data ----
    member_details_monthly_score = api_call(params, "prismMemberriskprofile")
    monthly_score_data = member_details_monthly_score["data"].get("riskSummary", [])
    user_list = member_details_monthly_score["data"].get("userlist", [])
    riskLevel = member_details_monthly_score["data"].get("riskLevel", [])

    # ---- Build structured data ----
    for row in monthly_score_data:
        care_user = row.get("Care_Coordinator_name", "UNKNOWN").strip()
        medicaid_id = row.get("medicaid_id")
        category = row.get("risk_category")
        subcat = row.get("sub_category_name")
        specific = row.get("sub_category2_name")
        date_str = row.get("to_date", "")
        score = float(row.get("score", 0) or 0)
        level = row.get("level", "N/A")

        # Clean date
        date_clean = date_str.split("T")[0] if "T" in date_str else date_str
        if date_clean and date_clean not in toDateArray:
            toDateArray.append(date_clean)

        # Build risk total per user/member/date
        member_total_risk.setdefault(care_user, {}).setdefault(medicaid_id, {}).setdefault(date_clean, 0)
        member_total_risk[care_user][medicaid_id][date_clean] += score

        # Build nested category hierarchy
        category_array \
            .setdefault(care_user, {}) \
            .setdefault(medicaid_id, {}) \
            .setdefault(category, {}) \
            .setdefault(subcat, {}) \
            .setdefault(specific, {})[date_clean] = {"score": score, "level": level}

    # ---- Sort dates chronologically ----
    if toDateArray:
        toDateArray = sorted(set(toDateArray), key=lambda d: datetime.strptime(d, "%m-%Y"))
        last_date = toDateArray[-1]
    else:
        last_date = None

    # ---- Flatten data for template ----
    for care_user, member_dict in category_array.items():
        for medicaid_id, cat_dict in member_dict.items():
            flat_category_array.setdefault(care_user, {}).setdefault(medicaid_id, [])
            for category, subcats in cat_dict.items():
                for subcat, specifics in subcats.items():
                    for specific, scores in specifics.items():
                        score_list = [
                            {"date": d, "score": v.get("score", "-"), "level": v.get("level", "N/A")}
                            for d, v in scores.items()
                        ]
                        flat_item = {
                            "category": category,
                            "sub_category": subcat,
                            "specific": specific,
                            "scores_list": score_list,
                        }
                        flat_category_array[care_user][medicaid_id].append(flat_item)
                        flat_for_template.append({
                            "user": care_user,
                            "member_id": medicaid_id,
                            "items": [flat_item],
                        })

    # ---- Group by dynamic risk levels ----
    for user, members in member_total_risk.items():
        risk_grouped.setdefault(user, {})
        # Initialize empty levels
        for rl in riskLevel:
            risk_grouped[user].setdefault(rl["level"], {})

        for member_id, scores in members.items():
            total = scores.get(last_date, 0)
            assigned_level = None

            for i, rl in enumerate(riskLevel):
                low, high = rl.get("range_from", 0), rl.get("range_to", 0)
                # Handle inclusive ranges correctly
                if (low <= total < high) or (i == len(riskLevel) - 1 and low <= total <= high):
                    assigned_level = rl["level"]
                    break

            if not assigned_level:
                assigned_level = riskLevel[-1]["level"]  # Fallback

            risk_grouped[user].setdefault(assigned_level, {})[member_id] = total

    # ---- Sort risk levels descending (LEVEL-3 → LEVEL-1) ----
    for user in risk_grouped:
        risk_grouped[user] = dict(sorted(
            risk_grouped[user].items(),
            key=lambda x: int(''.join(filter(str.isdigit, x[0])) or 0),
            reverse=True
        ))

    # ---- Count members per user ----
    user_member_counts = {}
    for user, levels in risk_grouped.items():
        member_ids = set()
        for members in levels.values():
            if isinstance(members, dict):
                member_ids.update(members.keys())
        user_key = user.replace(" ", "")
        user_member_counts[user_key] = len(member_ids)

    # ---- Render Template ----
    return render(request, "risk_profile.html", {
        "pageTitle": "MEMBER RISK PROFILE",
        "user_list": user_list,
        "toDateArray": toDateArray,
        "category_array": category_array,
        "member_total_risk": member_total_risk,
        "risk_grouped": risk_grouped,
        "user_id": request.POST.get("user_id"),
        "last_date": last_date,
        "flat_for_template": flat_for_template,
        "colspan_count": len(toDateArray) + 10,
        "user_member_counts": user_member_counts,
        "riskLevel": riskLevel,
    })

def download_users_csv(request):

    today = date.today()
    formatted_date = today.strftime("%m-%d-%Y")
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
    response['Content-Disposition'] = 'attachment; filename="RISK_GAPS_CIH_('+formatted_date+').CSV"'

    writer = csv.writer(response, delimiter='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)   # Write headers first
    writer.writerows(body)    # Then write all data rows

    return response