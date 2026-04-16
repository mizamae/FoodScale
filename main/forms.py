from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions,InlineRadios, AppendedText
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Column, Field, Fieldset
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

from .models import SiteSettings, WebContact

FORMS_LABEL_CLASS='section-subheading text-muted'
FORMS_FIELD_CLASS=''


class WebContactForm(forms.ModelForm):

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    class Meta:
        model = WebContact
        fields = ["name","email","phone","message"]
        widgets = {
            "message": forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super(WebContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = FORMS_LABEL_CLASS
        self.helper.field_class = FORMS_FIELD_CLASS
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        buttons=FormActions(
                            Submit('submitContact', _('Enviar'),css_class="btn btn-primary col-12"),
                        )
        for field in self.fields:
            if field != 'captcha': # to avoid changing the class of the captcha field (is used in JS)
                help_text = self.fields[field].help_text
                self.fields[field].help_text = None
                if help_text != '':
                    self.fields[field].widget.attrs.update({'class':'form-control','data-toggle':'tooltip' ,'title':help_text, 'data-bs-placement':'right', 'data-bs-container':'body'})
                else:
                    self.fields[field].widget.attrs.update({'class':'form-control'})
        
        fieldtype=''
        self.helper.layout = Layout(
            Field('name',type=fieldtype),
            Field('email',type=fieldtype),
            Field('phone',type=fieldtype),
            Field('message',type=fieldtype),
            Field('captcha',type=fieldtype),
            buttons,
            )
        
class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

    
class siteSettingsForm(forms.ModelForm):

    class Meta:
        model = SiteSettings
        exclude = []

    def __init__(self, *args, **kwargs):
        super(siteSettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.use_custom_control = True
        self.helper.label_class = FORMS_LABEL_CLASS
        self.helper.field_class = FORMS_FIELD_CLASS
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = True
        
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update({'class':'form-control','data-toggle':'tooltip' ,'title':help_text, 'data-bs-placement':'right', 'data-bs-container':'body'})
            else:
                self.fields[field].widget.attrs.update({'class':'form-control'})
        
        buttons=FormActions(
                        Div(
                        Column(Submit('submit', _('Guardar'),css_class="btn btn-primary col-12"),css_class="col-9"),
                        Column(HTML('<a href="{% url "home"  %}" class="btn btn-secondary col-12">'+str(_('Cancel'))+'</a>'),css_class="col-3"),
                        css_class="row")
                    )
        
        self.helper.layout = Layout(
                                    Fieldset(_("Installation details"),
                                        'INSTALLATION_NAME',
                                        'INSTALLATION_ADDR1',
                                        'INSTALLATION_ADDR2',
                                        'INSTALLATION_PHONE',
                                        'INSTALLATION_EMAIL',
                                        'PUBLISH_TO_WEB'
                                    ),
                                    Fieldset(_("Application details"),
                                        'VERSION_AUTO_UPDATE',
                                        'VERSION_CODE',
                                        'LAN_IP',
                                        AppendedText('SEC2LOGOUT', 's', active=True)
                                    ),

                                )
        self.helper.layout.append(buttons)