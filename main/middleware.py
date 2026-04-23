import datetime
from django.contrib.auth import logout
from django.conf import settings
    
class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.SEC2LOGOUT > 0:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            last_activity = request.session.get('last_activity', None)
            if last_activity:
                last_activity = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                # if (datetime.datetime.now() - last_activity).seconds > settings.SEC2LOGOUT: # timeout duration
                #     logout(request)
            if request.path != '/ping/': # to avoid updating last_activity with ping requests
                request.session['last_activity'] = current_time
        response = self.get_response(request)
        return response