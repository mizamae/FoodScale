from django.contrib.auth.models import UserManager
from django.utils.translation import gettext_lazy as _
import uuid

import logging
logger = logging.getLogger("users")

class CustomUserManager(UserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self,username=None, email=None, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        from .tasks import sendConfirmationEmail

        if email is None:
            raise ValueError('User must have an email address')
        if password is None or password=='':
            raise ValueError('User must have a not empty password')
        
        try:
            
            
            email = self.normalize_email(email)
            id = uuid.uuid4() 
            
            user = self.model(email=email, first_name=extra_fields.get('first_name',None), last_name=extra_fields.get('last_name',None), user_uuid=id,**extra_fields)

            user.set_password(password)

            user.save()
            sendConfirmationEmail.delay(user_uuid=user.user_uuid)
            
            logger.info('Created User ' + str(user))
        except Exception as exc:
            user = None
            logger.info('Error creating user ' + str(email) +'. ERROR: ' + str(exc))

        return user
    
    def create_superuser(self, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(**extra_fields)