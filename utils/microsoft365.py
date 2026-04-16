import requests
import json
import datetime
from django.conf import settings
import os
import base64
import logging
logger = logging.getLogger("email")

cache_file = "microsoft_credentials.json"

class Microsoft365_handler(object):
    @staticmethod
    def sendEmail(subject,recipients,html_content,attachments=None):               
        try:
            from O365 import Account,FileSystemTokenBackend

            credentials = (settings.O365_CLIENT_ID, settings.O365_CLIENT_SECRET)
            token_backend = FileSystemTokenBackend(token_path='.', token_filename=cache_file)

            account = Account(credentials, auth_flow_type='credentials', tenant_id=settings.O365_TENANT_ID,token_backend=token_backend)
            if account.authenticate():
                mailbox = account.mailbox(settings.EMAIL_HOST_USER)
                m = mailbox.new_message()
                m.to.add(settings.EMAIL_HOST_USER)
                if isinstance(recipients,list):
                    for rec in recipients:
                        m.bcc.add(rec)
                else:
                    m.bcc.add(recipients)
                m.subject = subject
                m.body = html_content
                m.save_message()
                if attachments:
                    for attachment in attachments:
                        m.attachments.add(attachment)
                        att = m.attachments[0]  # get the attachment object
                        # this is super important for this to work.
                        att.is_inline = True
                        att.content_id = attachment
                m.send()

        except requests.exceptions.RequestException as e:
            logger.exception("An error occurred while sending the email")

