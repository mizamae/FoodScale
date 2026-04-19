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

from .forms import SetPasswordForm, userSignUpForm, userWeightForm, userForm
from .models import User
import json
import logging
logger = logging.getLogger("users")

# Create your views here.

def permissionDenied(request):
    return TemplateResponse(request, 'UsersAPP/permission_denied.html',{})

def signUp(request):
    if request.method == 'POST':
        form = userSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return TemplateResponse(request, 'signUpOK.html')
        else:
            return TemplateResponse(request, 'signUp.html', {
                'form': form,
            })
    else:
        form = userSignUpForm()
    return TemplateResponse(request, 'signUp.html',{'form':form})


@login_required(login_url="login")
def myplace(request):
    if request.method == 'POST':
        form = userForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Datos guardados correctamente"))
        else:
            return TemplateResponse(request, 'myplace.html', {
                'form': form,
            })
    else:
        form = userForm(instance=request.user)
    return TemplateResponse(request, 'myplace.html',{'form':form})

def firstLogin(request,user_uuid):
    try:
        user = User.objects.get(user_uuid=user_uuid)
        user.activate()
    except:
        logger.error("User uuid does not exist " + str(user_uuid))
        return redirect('UsersAPP_permissionDenied')
    
    login(request, user)
    return redirect('home')


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_active,login_url='UsersAPP_permissionDenied')
def changePassword(request,):
    user = request.user
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.validate()
            messages.success(request, "Tu contraseña se ha cambiado correctamente")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return TemplateResponse(request, 'registration/password_reset_confirm.html', {'form': form,
                                                                        'form_title':_("Cambia tu contraseña")})


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
