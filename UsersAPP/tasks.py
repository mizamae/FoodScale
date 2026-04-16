import os
from .models import User
from django.conf import settings
from django.template.loader import get_template
from celery import shared_task
import logging
logger = logging.getLogger("celery")

from django.contrib.staticfiles import finders

@shared_task(bind=False,name='UsersAPP_sendConfirmationEmail')
def sendConfirmationEmail(user_uuid):
    user = User.objects.get(user_uuid=user_uuid)
    attachment = finders.find('logos/email.png')

    message = get_template("UsersAPP/_confirmationmail_template.html").render({
        'heading': "This email is to confirm an user account created at customer's portal",
        'link':user.confirmationLink,
        'image':os.path.basename(attachment),
        'username':user.get_username()
    })

    recipient=user.email
    subject = "Confirm the user account"
    
    if "gmail" in settings.EMAIL_HOST:
        from utils.googleGmail import googleGmail_handler
        googleGmail_handler.sendEmail(subject=subject,attachments=(attachment,),recipient=recipient,html_content=message)
    elif "office365" in settings.EMAIL_HOST:
        from utils.microsoft365 import Microsoft365_handler
        Microsoft365_handler.sendEmail(subject=subject,attachments=(attachment,),recipients=recipient,html_content=message)
    
    logger.info("Confirmation email sent to " + str(recipient))


@shared_task(bind=False,name='UsersAPP_loadDefaultObjects')
def loadDefaultObjects():
    from .models import User
    User.loadDefaultObjects()