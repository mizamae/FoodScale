from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages

from .forms import SetPasswordForm
from .models import User
import json
import logging
logger = logging.getLogger("users")

# Create your views here.

def permissionDenied(request):
    return render(request, 'UsersAPP/permission_denied.html',{})


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
    return render(request, 'registration/password_reset_confirm.html', {'form': form,
                                                                        'form_title':_("Setup your password for the first time")})

@login_required(login_url="login")
@user_passes_test(lambda u: u.validated,login_url='UsersAPP_permissionDenied')
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
    return render(request, 'registration/password_reset_confirm.html', {'form': form,
                                                                        'form_title':_("Change your password")})