import datetime
from django.conf import settings
from django.shortcuts import redirect

class AutoLogout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = datetime.datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed = (now - datetime.datetime.fromisoformat(last_activity)).total_seconds()
            if elapsed > getattr(settings, 'AUTO_LOGOUT_DELAY', 600):  # default 10 minutes
                from django.contrib.auth import logout
                logout(request)
                return redirect('login')  # redirect to your login page

        # Update last activity timestamp
        request.session['last_activity'] = now.isoformat()
        return self.get_response(request)
