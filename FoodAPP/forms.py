from django.forms import ModelForm, inlineformset_factory, ValidationError
from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from bootstrap_datepicker_plus.widgets import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions,AppendedText, PrependedText,Accordion, AccordionGroup,UneditableField, InlineField
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Column, Field,Fieldset
from crispy_forms.templatetags.crispy_forms_field import css_class

from .models import CombinationPosition,Ingredient, Meal, Diet
FORMS_LABEL_CLASS='col-8'
FORMS_FIELD_CLASS='col-4'

class CombinationPositionInTable(ModelForm):

    ingredientInput=forms.CharField()
    mealType=forms.ChoiceField(label=_("Tipo de comida"),choices = Meal.MEAL_TYPES,
                               help_text=_("Selecciona la comida del dia en la que añadir el alimento"),required=True)

    class Meta:
        model = CombinationPosition
        fields = ["quantity","ingredient"]
    
    def __init__(self, *args, **kwargs):
        editing = kwargs.pop('editing',False)
        super(CombinationPositionInTable, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = FORMS_LABEL_CLASS
        self.helper.field_class = FORMS_FIELD_CLASS
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.fields['ingredient'].disabled = editing
        self.fields['mealType'].disabled = editing
        self.fields['ingredientInput'].disabled = editing
        self.fields['ingredient'].required = not editing
        self.fields['mealType'].required = not editing
        if editing:
            self.fields['ingredientInput'].initial = self.fields['ingredient']
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update({'class':'form-control '+self.fields[field].widget.attrs['class'] if "class" in self.fields[field].widget.attrs else "",
                                                        'data-toggle':'tooltip' ,
                                                        'title':help_text, 
                                                        'data-bs-placement':'right', 
                                                        'data-bs-container':'body'})
            else:
                self.fields[field].widget.attrs.update({'class':'form-control'})
        
        self.helper.layout = Layout(
                                    Field('mealType',type=''),
                                    AppendedText('quantity','g',type=''),
                                    Field('ingredientInput',
                                          type="text"),
                                )
        
class DietForm(ModelForm):
    source=forms.CharField(label=_("Origen de los limites"),required=False)

    class Meta:
        model = Diet
        exclude = ['owner','values']
    
    def __init__(self, *args, **kwargs):
        super(DietForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = FORMS_LABEL_CLASS
        self.helper.field_class = FORMS_FIELD_CLASS
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = True
        
        self.helper.layout = Layout()
        
        values = self.instance.values
        self.fields['source'].initial = values['source']
        row = Div(css_class='row d-flex justify-content-center')
        row.append(Div(css_class="w-100 d-none d-md-block"))
        row.append(HTML('<h5>'+_("General")+'</h5>'))
        row.append(Field('description',type='text'))
        row.append(Field('source',type='text'))
        self.helper.layout.append(row)
        
        for nutrient in values["nutrients"]:
            row = Div(css_class='row d-flex justify-content-center')
            row.append(Div(css_class="w-100 d-none d-md-block"))
            row.append(HTML('<h5>'+nutrient['name']+'</h5>'))
            for item in nutrient['nutrients']:
                self.fields[nutrient['name']+"_"+item['name']] = forms.FloatField(label=item['name'],required = False,initial = item['quant'],disabled=False)
                row.append(AppendedText(nutrient['name']+"_"+item['name'],item['unit']))
            self.helper.layout.append(row)
        
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update({'class':'form-control '+self.fields[field].widget.attrs['class'] if "class" in self.fields[field].widget.attrs else "",
                                                        'data-toggle':'tooltip' ,
                                                        'title':help_text, 
                                                        'data-bs-placement':'right', 
                                                        'data-bs-container':'body'})
            else:
                self.fields[field].widget.attrs.update({'class':'form-control'})
        
        

        buttons=Div(
                    Div(css_class="w-100 d-none d-md-block"),
                    Div(
                        Column(Submit('submit', _('Save'),css_class="btn btn-primary col-12"),css_class="col-6"),
                        Column(HTML('<a href="{% url "home" %}" class="btn btn-light col-12">'+str(_('Cancel'))+'</a>'),css_class="col-6"),
                        css_class="row"
                    ),
                    css_class="row d-flex justify-content-center"
                    )
        
        
        self.helper.layout.append(buttons)

    def clean(self,):
        cleaned_data = super(DietForm, self).clean()
        for field in cleaned_data:
            print(field)

        

class CombinationPositionInlineForm(ModelForm):
    class Meta:
        model = CombinationPosition
        fields = ["quantity","ingredient"]
    
    def __init__(self, *args, **kwargs):
        meal = kwargs.pop('meal',None)
        super(CombinationPositionInlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = FORMS_LABEL_CLASS
        self.helper.field_class = FORMS_FIELD_CLASS
        self.helper.form_class = 'form-inline'
        #self.helper.template = "bootstrap4/table_inline_formset.html"
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.fields['ingredient'].disabled=False
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update({'class':'form-control '+self.fields[field].widget.attrs['class'] if "class" in self.fields[field].widget.attrs else "",
                                                        'data-toggle':'tooltip' ,
                                                        'title':help_text, 
                                                        'data-bs-placement':'right', 
                                                        'data-bs-container':'body'})
            else:
                self.fields[field].widget.attrs.update({'class':'form-control'})
        
        self.helper.layout = Layout(
                                    AppendedText('quantity','g',type=''),
                                    Field('ingredient',type='search'),
                                )


CombinationPositionFormSet = inlineformset_factory(Ingredient,CombinationPosition, fk_name="ingredient",fields = ["quantity","ingredient"],
                                           form=CombinationPositionInlineForm,extra=0,can_delete=True)