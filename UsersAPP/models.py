from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import json
from django.conf import settings
import os
from .managers import CustomUserManager
from pywebpush import webpush
from django.contrib.staticfiles import finders


CONFIRMATION_URL = "https://"+settings.PAGE_DNS+"/userapp/firstlogin/"

class User(AbstractBaseUser):

    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True,null=True)

    first_name = models.CharField(_("Nombre"), max_length=150, blank=True,null=True)
    last_name = models.CharField(_("Apellido"), max_length=150, blank=True,null=True)
    email = models.EmailField(_("Email"), unique=True,max_length=255,)

    is_vip = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_subscribed = models.BooleanField(default=False)

    data = models.JSONField(blank=True,null=True)
    
    timezone = models.CharField(max_length=255, default = settings.TIME_ZONE )

    groups = models.ManyToManyField(Group)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        permissions=(
        )

    def __str__(self):
        return self.email

    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
    
    def sendNotification(self,title,body,redirect="https://" + settings.PAGE_DNS+"/"):
        if self.is_subscribed:
            webpush(subscription_info=self.subscription_info,
                data=json.dumps({'title':title,'body':body,
                            'badge':finders.find('site/logos/CompanyLogoEmail.png'),
                            'icon':finders.find('site/ico/favicon.ico'),
                            'redirect':redirect
                            }),
                vapid_private_key=settings.PUSH_NOTIFICATIONS_SETTINGS["WP_PRIVATE_KEY"],
                vapid_claims=settings.PUSH_NOTIFICATIONS_SETTINGS["WP_CLAIMS"])

    def sendBreakfastNotification(self,):
        self.sendNotification(title=_("Recuerda registrar tu desayuno"),
                              body=_("Ey! esto solo es un recordatorio de que tienes que registrar tu desayuno"),
                              redirect="https://" + settings.PAGE_DNS+"/foodapp/calculator/0")

    def sendLunchNotification(self,):
        self.sendNotification(title=_("Recuerda registrar tu comida"),
                              body=_("Ey! esto solo es un recordatorio de que tienes que registrar tu comida"),
                              redirect="https://" + settings.PAGE_DNS+"/foodapp/calculator/0")


    def registerWeight(self,value,dateTime=None):
        if dateTime is None:
            dateTime = timezone.now().replace(microsecond=0)
        else:
            dateTime = dateTime.replace(microsecond=0)
        register = {'timestamp':dateTime.isoformat(),'value':value}
        if self.data is None:
            self.data={'weight':[]}
        self.data['weight'].append(register)
        self.save(update_fields=['data',])

    @property
    def subscription_info(self,):
        return self.data['subscription_info']
    
    @property
    def notifications(self,):
        return self.is_subscribed
    
    def activateNotifications(self, info):
        self.is_subscribed = True
        if self.data is None:
            self.data={}
        self.data['subscription_info']=info   
        self.save(update_fields=['is_subscribed','data'])

    def deactivateNotifications(self,):
        self.is_subscribed = False
        self.data['subscription_info']=None   
        self.save(update_fields=['is_subscribed','data'])

    @property
    def confirmationLink(self):
        if not self.is_active:
            return CONFIRMATION_URL+str(self.user_uuid)
        
    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        else:
            return self.get_username()
        
    def activate(self):
        #self.set_password(password)
        self.is_active = True
        self.save(update_fields=['is_active',])
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
                    

