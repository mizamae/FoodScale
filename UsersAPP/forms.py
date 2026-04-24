from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Column, Field
from django.utils.translation import gettext as _
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django.utils import timezone

from .models import User

from timezones.forms import TimeZoneField

FORMS_LABEL_CLASS='col'
FORMS_FIELD_CLASS='col'


class userSignUpForm(forms.ModelForm):

    password1 = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Contraseña (confirmación)'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name','email','password1','password2']
        widgets = {
        }
    def __init__(self, *args, **kwargs):
        super(userSignUpForm, self).__init__(*args, **kwargs)
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
                    Column(Submit('submit', _('Save'),css_class="btn btn-primary col-12"),css_class="col-9"),
                    Column(HTML('<a href="{% url "home" %}" class="btn btn-light col-12">'+str(_('Cancel'))+'</a>'),css_class="col-3"),
                    css_class="row")
                    )
        
        self.helper.layout = Layout(
                                Field('first_name',type=''),
                                Field('last_name',type=''),
                                Field('email',type=''),
                                Field('password1',type=''),
                                Field('password2',type=''),
                                )
            
        self.helper.layout.append(buttons)

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(**cleaned_data)
        return user

class userForm(forms.ModelForm):

    timezone = TimeZoneField(label=_("Franja horaria"))
    class Meta:
        model = User
        fields = ['first_name', 'last_name','email','timezone']
        widgets = {
        }
    class Media:
        js = ('userform.js',)

    def __init__(self, *args, **kwargs):
        super(userForm, self).__init__(*args, **kwargs)
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
                    Column(Submit('submit', _('Save'),css_class="btn btn-primary col-12"),css_class="col-9"),
                    Column(HTML('<a href="{% url "home" %}" class="btn btn-light col-12">'+str(_('Cancel'))+'</a>'),css_class="col-3"),
                    css_class="row")
                    )
        
        self.helper.layout = Layout(
                                Field('first_name',type=''),
                                Field('last_name',type=''),
                                Field('email',type=''),
                                Field('timezone',type=''),
                                )
            
        self.helper.layout.append(buttons)

class userWeightForm(forms.Form):
    dateTime = forms.DateTimeField(initial=timezone.now())
    value=forms.CharField(label=_("Medida"),help_text=_("Medida en kg"),required=True)

    class Meta:
        widgets = {
            "dateTime": DateTimePickerInput(options={"format": "DD/MM/YYYY HH:mm"}),
        }

    def __init__(self, *args, **kwargs):
        super(userWeightForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.use_custom_control = True
        self.helper.label_class = FORMS_LABEL_CLASS
        self.helper.field_class = FORMS_FIELD_CLASS
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        