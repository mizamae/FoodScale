from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from .managers import CustomUserManager

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

    data = models.JSONField(blank=True,null=True)
    
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
    
                    

