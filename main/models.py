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

class SingletonModel(models.Model):
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()
    
    def set_cache(self):
        cache.set(self.__class__.__name__, self)
    
    @classmethod
    def checkIfExists(cls):
        try:
            obj = cls.objects.get(pk=1)
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            obj.set_cache()
        return cache.get(cls.__name__)
    
class SiteSettings(SingletonModel):
    class Meta:
        verbose_name = _('Configuration')
        verbose_name_plural = _('Configurations')

    INSTALLATION_NAME = models.CharField(verbose_name=_('Name of the installation'),max_length=100,
                                    help_text=_('The name of the installation'),default='My installation')
    INSTALLATION_ADDR1 = models.CharField(verbose_name=_('Address of the installation'),max_length=200,
                                    help_text=_('The address of the installation'),default='My street and number')
    INSTALLATION_ADDR2 = models.CharField(verbose_name=_('Address of the installation (Line 2)'),max_length=200,
                                    help_text=_('The address of the installation'),blank=True,null=True)
    INSTALLATION_PHONE = models.CharField(verbose_name=_('Phone of the installation'),max_length=200,
                                    help_text=_('The phone number of the installation'),blank=True,null=True)
    INSTALLATION_EMAIL = models.EmailField(verbose_name=_('Contact email of the installation'),
                                    help_text=_('The contact email of the installation'),blank=True,null=True)
    
    PUBLISH_TO_WEB = models.BooleanField(verbose_name=_('Publish products update to the web'),
                                    help_text=_("Enables publishing any product creation/update to the installation's web to keep it updated"),default=False)
    
    VERSION_AUTO_UPDATE=models.BooleanField(verbose_name=_('Automatic updates'),
                                help_text=_('Allows to automatically update the software from official repository (requires internet access)'),default=False)
    VERSION_CODE= models.CharField(verbose_name=_('Code of the current version'),
                                max_length=10,default='',blank=True)

    LAN_IP = models.GenericIPAddressField(blank=True, null=True)

    SEC2LOGOUT = models.PositiveSmallIntegerField(verbose_name=_("Seconds to logout"),default=0,
                                                 help_text=_("Seconds after when, the user would need to login again"))
    
    @classmethod
    def runOnInit(cls):
        connected = cls.checkInternetConnection()
        IP=cls.getMyLANIP()
        SETTINGS=cls.load()
        if IP != SETTINGS.LAN_IP:
            SETTINGS.LAN_IP = IP
            SETTINGS.save(update_fields=['LAN_IP',])
        
        from git import Repo
        repo = Repo(settings.GIT_PATH)
        res=repo.remotes.origin.pull('main')
        try:
            rev_code = res[0].commit.name_rev
        except: 
            rev_code = 'unknown'
        if rev_code[0:7] != SETTINGS.VERSION_CODE:
            SETTINGS.VERSION_CODE = rev_code[0:7]
            SETTINGS.save(update_fields=['VERSION_CODE',])       

    @staticmethod
    def checkInternetConnection():
        import requests
        try:
            r = requests.get('http://google.com',timeout=1)
            if r.status_code==200:
                return True
            else:
                return False
        except: 
            return False
    
    @staticmethod
    def getMyLANIP():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('192.0.0.8', 1027))
        except socket.error:
            return None
        return s.getsockname()[0]