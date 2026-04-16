from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.template.response import TemplateResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import datetime

from .forms import SetPasswordForm, userWeightForm
from .models import User
import json
import logging
logger = logging.getLogger("users")

# Create your views here.

def permissionDenied(request):
    return TemplateResponse(request, 'UsersAPP/permission_denied.html',{})

@login_required(login_url="login")
def myplace(request):

    return TemplateResponse(request, 'myplace.html')

def firstLogin(request,user_uuid):
    try:
        user = User.objects.get(user_uuid=user_uuid)
    except:
        logger.error("User uuid does not exist " + str(user_uuid))
        return redirect('UsersAPP_permissionDenied')
    
    login(request, user)
    return redirect('UsersAPP_changePasswordFirstTime',user_uuid=user.user_uuid)

@login_required(login_url="login")
def changePasswordFirstTime(request,user_uuid):
    user = request.user

    if user.user_uuid != user_uuid:
        logger.error("User uuid does not coincide with user's " + str(user_uuid) + " against " + str(user.user_uuid))
        return redirect('UsersAPP_permissionDenied')
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.validate()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return TemplateResponse(request, 'registration/password_reset_confirm.html', {'form': form,
                                                                        'form_title':_("Setup your password for the first time")})

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_active,login_url='UsersAPP_permissionDenied')
def changePassword(request,):
    user = request.user
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.validate()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return TemplateResponse(request, 'registration/password_reset_confirm.html', {'form': form,
                                                                        'form_title':_("Change your password")})


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_active,login_url='UsersAPP_permissionDenied')
def addWeight(request,dayOffset):
    day = datetime.date.today() + datetime.timedelta(days=dayOffset)
    MyTime = datetime.datetime.now().time().replace(microsecond=0)
    dateTime=datetime.datetime.combine(day, MyTime)
    dateTime = timezone.make_aware(dateTime)
    if request.method == "POST":
        form = userWeightForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data.get('value')
            
            dateTime = form.cleaned_data.get('dateTime')
            request.user.registerWeight(value,dateTime=dateTime)
            return HttpResponse(
                        status=204,
                        headers={
                            'HX-Trigger': json.dumps({
                                "showMessage": f"Medición de peso registrado."
                            })
                        })
        else:
            return TemplateResponse(request, 'UsersAPP/weightForm.html', {
                'form': form,
            })
    else:
        form = userWeightForm(initial={'dateTime':timezone.localtime(dateTime)})
    return TemplateResponse(request, 'UsersAPP/weightForm.html', {
        'form': form,
    })
