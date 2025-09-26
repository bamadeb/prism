import random
import requests ,json,re

#from .utils import send_email
import time
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime, timedelta, timezone
from datetime import datetime, date
from django.shortcuts import render, redirect
import uuid
import csv
import io
def api_call(params, funName):
    api_url = settings.API_URL + funName
    response = requests.post(api_url, json=params)
    return response.json()
def home(request):
    return HttpResponse("Hello, World!")
def processmember(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    session_id = ""
    logList = {}
    if request.POST.get("session_id"):
        session_id = request.POST.get("session_id")
        process_btn = request.POST.get("processBTN")  # name of your button
        data = {
            'session_id': session_id
        }
        if session_id :
            logResult = api_call(data, "prismProcessMembersSeccionID"+"-"+settings.ENVIRONMENT)
            #logResult = response.json()
            print(logResult)
            session_id = int(time.time())
            logList = logResult['data']['loglist']
            for log in logList:
                if isinstance(log["LOG_DATE"], str):
                    log["LOG_DATE"] = datetime.fromisoformat(
                        log["LOG_DATE"].replace("Z", "+00:00")
                    )
    else:
        session_id = int(time.time())
    if request.method == "POST" and 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        decoded_file = uploaded_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        # convert rows to list of dicts
        insertDataArray = []
        date_fields = [
            "DT_OF_BIRTH",
            "ENROLL_DT",
            "PCP_EFF_DT_S"
        ]
        other_dates = [
            "PCP_EFF_DT_E",
            "PLAN_DT_S",
            "PLAN_DT_E",
            "DISENROLL_DT"
        ]
        for row in reader:
            for field in date_fields:
                if field in row:
                    row[field] = clean_date(row[field])
            for field in other_dates:
                if field in row:
                    row.pop(field)
            row['INSERT_SESSION_ID'] = session_id
            insertDataArray.append(row)
        # --- Helper to split into batches of 1000 ---
        def chunked(iterable, size=1000):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]

        # --- Insert Members ---
        for batch_num, batch in enumerate(chunked(insertDataArray, 1000), start=1):
            print(f"Processing MEM_MEMBERS batch {batch_num}, rows: {len(batch)}")
            apidata = {
                "table_name": "MEM_MEMBERS_TEMP",
                "insertDataArray": batch,
            }
            insertresult = api_call(apidata, "prismMultipleRowInsert"+"-"+settings.ENVIRONMENT)
            print(insertresult)
    apidata = {
        "session_id": session_id
    }
    exist_count = 0
    error_count = 0
    totalRecords = 0
    tempMemberList = {}
    if request.method == "POST":
        tempMember = api_call(apidata, "prismGetTempMembersBySeccionID"+"-"+settings.ENVIRONMENT)
        tempMemberList = tempMember['data']
        totalRecords = tempMember['totalRecords']
        # print(tempMemberList)
        for member in tempMemberList:
            # print(activity)
            if member["exist_member"]:
                exist_count += 1
            if member["SUBSCRIBER_ID"] is None or str(member["SUBSCRIBER_ID"]).strip() == "":
                error_count += 1
            dob = member.get("DT_OF_BIRTH")
            if isinstance(dob, str):
                member["DT_OF_BIRTH"] = datetime.fromisoformat(dob.replace("Z", "+00:00"))
    #print(logList)
    return render(request, 'processmember.html', {
        'pageTitle': "PROCESS MEMBER",
        'session_id': session_id,
        'tempMember' : tempMemberList,
        'totalTempMemberCount' : totalRecords,
        'exist_count': exist_count,
        'logList': logList,
        'error_count': error_count
    })
def processriskgap(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    session_id = ""
    logList = {}
    if request.POST.get("session_id"):
        session_id = request.POST.get("session_id")
        process_btn = request.POST.get("processBTN")  # name of your button
        data = {
            'session_id': session_id
        }
        if session_id :
            logResult = api_call(data, "prismProcessRiskGapsSeccionID"+"-"+settings.ENVIRONMENT)
            #logResult = response.json()
            session_id = int(time.time())
            logList = logResult['data']['loglist']
            for log in logList:
                if isinstance(log["LOG_DATE"], str):
                    log["LOG_DATE"] = datetime.fromisoformat(
                        log["LOG_DATE"].replace("Z", "+00:00")
                    )
    else:
        session_id = int(time.time())
    if request.method == "POST" and 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        decoded_file = uploaded_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        # convert rows to list of dicts
        insertDataArray = []
        date_fields = [
            "RELEVANT_DATE"
        ]
        other_dates = []
        for row in reader:
            for field in date_fields:
                if field in row:
                    row[field] = clean_date(row[field])
            for field in other_dates:
                if field in row:
                    row.pop(field)
            row['INSERT_SESSION_ID'] = session_id
            insertDataArray.append(row)
        # --- Helper to split into batches of 1000 ---
        def chunked(iterable, size=1000):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]

        # --- Insert Members ---
        for batch_num, batch in enumerate(chunked(insertDataArray, 1000), start=1):
            print(f"Processing MEM_RISK_GAP_TEMP batch {batch_num}, rows: {len(batch)}")
            apidata = {
                "table_name": "MEM_RISK_GAP_TEMP",
                "insertDataArray": batch,
            }
            insertresult = api_call(apidata, "prismMultipleRowInsert"+"-"+settings.ENVIRONMENT)
            #insertR = insertresult.json()
            #print(insertresult)
    exist_count = 0
    error_count = 0
    tempRiskGapsList = {}
    totalRecords = 0
    if request.method == "POST":
        apidata = {
            "session_id": session_id
        }
        tempRiskGapsResponse = api_call(apidata, "prismGetTempRiskGapsBySeccionID"+"-"+settings.ENVIRONMENT)
        #print(tempRiskGapsResponse)
        tempRiskGapsList = tempRiskGapsResponse['data']
        totalRecords = tempRiskGapsResponse['totalRecords']
        #print(tempRiskGapsList)
        for member in tempRiskGapsList:
            # print(activity)
            if member["member_exist"] is None or str(member["member_exist"]).strip() == "":
                error_count += 1
            elif member["exist_gap"]:
                exist_count += 1
            RELEVANT_DATE = member.get("RELEVANT_DATE")
            if isinstance(RELEVANT_DATE, str):
                member["RELEVANT_DATE"] = datetime.fromisoformat(RELEVANT_DATE.replace("Z", "+00:00"))
    #print(logList)
    return render(request, 'processriskgap.html', {
        'pageTitle': "PROCESS RISK GAP",
        'session_id': session_id,
        'tempRiskGapsList' : tempRiskGapsList,
        'totalTempRiskGapsCount' : totalRecords,
        'exist_count': exist_count,
        'logList': logList,
        'error_count': error_count
    })
def processquality(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    session_id = ""
    logList = {}
    if request.POST.get("session_id"):
        session_id = request.POST.get("session_id")
        process_btn = request.POST.get("processBTN")  # name of your button
        data = {
            'session_id': session_id
        }
        if session_id :
            logResult = api_call(data, "prismProcessQualityGapsSeccionID"+"-"+settings.ENVIRONMENT)
            #logResult = response.json()
            #print("Log result" + session_id)
            #print(logResult)
            session_id = int(time.time())
            logList = logResult['data']['loglist']
            for log in logList:
                if isinstance(log["LOG_DATE"], str):
                    log["LOG_DATE"] = datetime.fromisoformat(
                        log["LOG_DATE"].replace("Z", "+00:00")
                    )
    else:
        session_id = int(time.time())
    if request.method == "POST" and 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        decoded_file = uploaded_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        # convert rows to list of dicts
        insertDataArray = []
        date_fields = ["Date_of_Birth"]  # use normalized names
        other_dates = []

        for row in reader:
            # normalize all keys: replace spaces with underscores
            normalized_row = {k.replace(" ", "_"): v for k, v in row.items()}

            # clean date fields
            for field in date_fields:
                if field in normalized_row:
                    normalized_row[field] = clean_date(normalized_row[field])

            # remove unwanted date fields
            for field in other_dates:
                normalized_row.pop(field, None)

            normalized_row["INSERT_SESSION_ID"] = session_id
            insertDataArray.append(normalized_row)

        # --- Helper to split into batches of 1000 ---
        def chunked(iterable, size=1000):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]

        # --- Insert Members ---
        for batch_num, batch in enumerate(chunked(insertDataArray, 1000), start=1):
            print(f"Processing MEM_RISK_GAP_TEMP batch {batch_num}, rows: {len(batch)}")
            apidata = {
                "table_name": "MEM_CIH_QUALITY_TEMP",
                "insertDataArray": batch,
            }
            insertresult = api_call(apidata, "prismMultipleRowInsert"+"-"+settings.ENVIRONMENT)
            #insertR = insertresult.json()
            #print(insertresult)
    exist_count = 0
    error_count = 0
    tempQualityGapsList = {}
    totalRecords = 0
    if request.method == "POST":
        apidata = {
            "session_id": session_id
        }
        tempQualityGaps = api_call(apidata, "prismGetTempQualityGapsBySeccionID"+"-"+settings.ENVIRONMENT)
        #tempQualityGaps = tempQualityGapsResponse.json()
        #print(tempQualityGaps)
        tempQualityGapsList = tempQualityGaps['data']
        #print(tempRiskGapsList)
        totalRecords = tempQualityGaps['totalRecords']
        for quality in tempQualityGapsList:
            # print(activity)
            if quality["member_exist"] is None or str(quality["member_exist"]).strip() == "":
                error_count += 1
            elif quality["quality_gaps_exist"]:
                exist_count += 1
            dob = quality.get("Date_of_Birth")
            if isinstance(dob, str):
                quality["Date_of_Birth"] = datetime.fromisoformat(dob.replace("Z", "+00:00"))
    #print(tempQualityGapsList)
    return render(request, 'processquality.html', {
        'pageTitle': "PROCESS QUALITY GAP",
        'session_id': session_id,
        'tempQualityGapsList' : tempQualityGapsList,
        'totalTempQualityGapsCount' : totalRecords,
        'exist_count': exist_count,
        'logList': logList,
        'error_count': error_count
    })
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

