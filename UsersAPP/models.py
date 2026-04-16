from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from .managers import CustomUserManager

CONFIRMATION_URL = "https://"+settings.PAGE_DNS+"/users/firstlogin/"

class User(AbstractUser):

    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True,null=True)

    first_name = models.CharField(_("Nombre"), max_length=150, blank=True,null=True)
    last_name = models.CharField(_("Apellido"), max_length=150, blank=True,null=True)
    email = models.EmailField(_("Email"), unique=True)

    # products = models.ManyToManyField('ProductsAPP.Product',related_name="users",verbose_name=_("Products enabled"),blank=True)
    # apps = models.ManyToManyField('ExternalAPPs.ExternalAPP',related_name="users",verbose_name=_("Apps enabled"),blank=True)

    is_vip = models.BooleanField(default=False)

    data = models.JSONField(blank=True,null=True)
    
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
        
    def validate(self):
        #self.set_password(password)
        self.validate = True
        self.save(update_fields=['validate',])
    
                    

