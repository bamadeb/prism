from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
def processlogreport(request):
    if not request.session.get('is_logged_in', False):
        return render(request, 'login.html')

    return render(request, 'processlogreport.html', {
        'pageTitle': "FILE PROCESS LOG REPORT",
    })
