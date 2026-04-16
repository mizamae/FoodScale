from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponse
import datetime

import json
from django.db.models import Q
User=get_user_model()

from .forms import SetPasswordForm, siteSettingsForm, WebContactForm
from .models import SiteSettings

def home(request):
    return TemplateResponse(request, 'home.html',{ 'contactForm':WebContactForm()})

@login_required(login_url="login")
def myplace(request):

    return TemplateResponse(request, 'myplace.html')

def contact(request):
    if request.method == 'POST':
        form = WebContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "Formulario recibido, nos pondremos en contacto contigo a la mayor brevedad posible")
        else:
            messages.warning(request, "Falta algún dato en el formulario")
        return redirect(reverse('home')+"#contact")
    else:
        return HttpResponse(status=404,content=json.dumps({}))
    
@login_required(login_url="login")
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return TemplateResponse(request, 'registration/password_reset_confirm.html', {'form': form})


@login_required(login_url="login")
def siteSettings(request):
    user = request.user
    if request.method == 'POST':
        form = siteSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Global settings have been saved")
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = siteSettingsForm(instance = SiteSettings.load())
    return TemplateResponse(request, 'form.html', {'title':"Global settings",'form': form})