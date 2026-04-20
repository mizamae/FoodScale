from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
User=get_user_model()

from django.conf import settings
from django.http import HttpResponse
import datetime

import json
from django.db.models import Q


from .forms import  WebContactForm

def home(request):
    return TemplateResponse(request, 'home.html',{ 'contactForm':WebContactForm()})

def privacy(request):
    return TemplateResponse(request, 'privacy_policy.html',)

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
    


