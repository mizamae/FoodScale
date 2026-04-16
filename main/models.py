from django.core.cache import cache
from django.db import models
from django.db.utils import OperationalError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import logging
logger = logging.getLogger("models")

class WebContact(models.Model):
    name = models.CharField(_("Name"), max_length=150)
    email = models.EmailField(_("Email address"))
    phone = models.CharField(_("Phone number"), max_length=20, blank=True,null=True)
    message = models.TextField()
    is_responded = models.BooleanField(default=False)

