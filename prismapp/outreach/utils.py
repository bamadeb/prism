import requests
from django.conf import settings

def api_call(params, funName):
    api_url = settings.API_URL + funName +"-"+settings.ENVIRONMENT
    response = requests.post(api_url, json=params)
    return response.json()

def fetch_add_action_master_data():
    #response = requests.get("https://example.com/api/master-data")
    data = {

    }
    response = api_call(data, "prismGetAddActionMasterData")
    return response