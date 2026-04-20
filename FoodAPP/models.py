from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import os
from django.core.files.storage import FileSystemStorage
from PIL import Image, ExifTags
import jmespath

FILE_DIR = os.path.join(settings.MEDIA_ROOT)
IMAGES_FILESYSTEM = FileSystemStorage(location=FILE_DIR,base_url=settings.MEDIA_URL)

class ModelWithImage(models.Model):

    class Meta:
        abstract = True

    picture = models.ImageField(_('Imagen'),null=True,blank=True,storage=IMAGES_FILESYSTEM)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cached_picture_path = self.picture.path if self.picture else None

    def save(self, *args, **kwargs):
        if self.picture and self.cached_picture_path != self.picture.path:
            self.compress_image(source_field='picture', target_field='picture', size=200)
        super().save(*args, **kwargs)

    # Method for image compression
    def compress_image(self, source_field, target_field, size):
        if not getattr(self, source_field):
            # If the source_field is empty, no need to proceed
            return
        # Open the original image
        img = Image.open(getattr(self, source_field))
        # Check for EXIF orientation and rotate if necessary
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                try:
                    exif = dict(img._getexif().items())
                    if exif[orientation] == 3:
                        img = img.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        img = img.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        img = img.rotate(90, expand=True)
                except (AttributeError, KeyError, IndexError):
                    # No EXIF data or invalid data, don't perform rotation
                    pass
        # Calculate the aspect ratio to maintain proportions when resizing
        aspect_ratio = img.width / img.height
        # Resize the image to the specified size
        img = img.resize((size, int(size / aspect_ratio)))
        # Convert the image to RGB mode if it's in RGBA mode
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        # Save the compressed image to the target_field's upload_to path inside MEDIA_ROOT
        target_upload_to = getattr(self.__class__, target_field).field.upload_to

        img_path = getattr(self, source_field).path
        img_name, img_ext = os.path.splitext(os.path.basename(img_path))
        unique_id = str(uuid.uuid4())
        compressed_img_name = f'{img_name}{unique_id}_{size}{img_ext}'
        compressed_img_path = os.path.join(settings.MEDIA_ROOT, target_upload_to, compressed_img_name)
        # Ensure that the target directory exists before saving
        os.makedirs(os.path.dirname(compressed_img_path), exist_ok=True)
        # Save the image as JPEG
        img.save(compressed_img_path, 'JPEG')
        img.close()
        #os.remove(getattr(self, source_field).path)
        # Set the target_field with the compressed image path relative to MEDIA_ROOT
        setattr(self, target_field, os.path.relpath(compressed_img_path, settings.MEDIA_ROOT))

class IngredientFamily(ModelWithImage):
    class Meta:
        verbose_name = _('Familia de alimentos')
        verbose_name_plural = _('Familias de alimentos')
        ordering = ['name']

    name = models.CharField(max_length=30, unique=True,verbose_name=_("Name"))
    short_description = models.CharField(_("Descripcion breve"), max_length=300)
    long_description = models.CharField(_("Descripcion detallada"), max_length=1000)

    def __str__(self) -> str:
        return self.name
    
    @property
    def itemCount(self):
        return self.ingredients.count()
    
class Ingredient(ModelWithImage):
    id = models.PositiveBigIntegerField(editable=False,primary_key=True)
    family = models.ForeignKey(IngredientFamily, on_delete=models.CASCADE, related_name='ingredients', blank = True, null=True)  

    name = models.CharField(max_length=150, verbose_name=_("Nombre"),unique=True)
    description = models.CharField(max_length=150, verbose_name=_("Descripcion"),default="",blank=True)
    nutrients = models.JSONField(blank=True,null=True)

    class Meta:
        ordering=['name',]

    def __str__(self) -> str:
        return self.name
    
    @property
    def basicInfo(self):
        """Returns the basic nutritional information of the ingredient per 100g"""
        result =[]
        if self.nutrients:
            result = self.nutrients['proximales']+self.nutrients['hidratos de carbono']            
        return result
    
    def scaledBasicInfo(self,weight):
        result = self.basicInfo
        for nutrient in result:
            nutrient['quant'] = round(nutrient['quant']*weight/100,2)
        return result


class CombinationPosition(models.Model):
    class Meta:
        verbose_name = _('Combinacion de ingredientes')
        verbose_name_plural = _('Combinaciones de ingredientes')

    
    meal = models.ForeignKey("Meal", on_delete=models.CASCADE, related_name='resultant_product')
    quantity = models.FloatField(default=1,verbose_name=_("Cantidad en gramos"))
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='isUsedIn',verbose_name=_("Ingrediente"))

    def __str__(self) -> str:
        return str(self.ingredient)
    
    @property
    def scaledBasicInfo(self,):
        return self.ingredient.scaledBasicInfo(weight=self.quantity)
    
    @property
    def scale(self,):
        """All the data is referred to 100 g of ingredient"""
        return self.quantity/100
    
    def updateQuantity(self,newQuantity):
        self.quantity = newQuantity
        self.save(update_fields=['quantity',])
    
class Meal(models.Model):
    TYPE_BREAKFAST = 0
    TYPE_BRUNCH = 1
    TYPE_LUNCH = 2
    TYPE_AFTERLUNCH = 3
    TYPE_DINNER = 4
    TYPE_AFTERDINNER = 5
    MEAL_TYPES = (
        (TYPE_BREAKFAST, _("Desayuno")),
        (TYPE_BRUNCH, _("Almuerzo")),
        (TYPE_LUNCH, _("Comida")),
        (TYPE_AFTERLUNCH, _("Merienda")),
        (TYPE_DINNER, _("Cena")),
        (TYPE_AFTERDINNER, _("Despues de cena")),
    )
    type = models.PositiveSmallIntegerField(choices=MEAL_TYPES,verbose_name=_("Tipo de comida"),
                                            help_text=_("Determina el tipo de comida en el dia"))
    components = models.ManyToManyField('Ingredient',blank=True,through='CombinationPosition')

    dateTime = models.DateTimeField(verbose_name=_("Date and time"))
    owner = models.ForeignKey(User,on_delete=models.CASCADE,editable = False)

    @property
    def totalQuantity(self):
        total=0
        for pos in self.ingredients:
            total += pos.quantity
        return total
    
    @property
    def ingredients(self):
        return CombinationPosition.objects.filter(meal=self)
    
    @property
    def nutritionalInfoBasic(self):
        overall = []
        for combination in self.ingredients:
            data = combination.scaledBasicInfo
            overall = Meal.accumulateListOfDictionaries(list1=overall,list2=data)
        return overall
    
    def appendIngredient(self,quantity,ingredient):
        try:
            pos = CombinationPosition.objects.get(meal=self,ingredient=ingredient)
            pos.quantity+=quantity
            pos.save()
        except CombinationPosition.DoesNotExist:
            pos = CombinationPosition.objects.create(meal=self,ingredient=ingredient,quantity=quantity)
    
    def getQuantityIngredient(self,ingredient):
        try:
            pos = CombinationPosition.objects.get(meal=self,ingredient=ingredient)
            return pos.quantity
        except CombinationPosition.DoesNotExist:
            return 0
    
    @staticmethod
    def accumulateDailyQuantity(day,user):
        meals = Meal.objects.filter(dateTime__date=day,owner=user)
        result=0
        for meal in meals:
            result += meal.totalQuantity
        return result

    @staticmethod
    def accumulateDailyNutrients(day,user):
        meals = Meal.objects.filter(dateTime__date=day,owner=user)
        result=[]
        for meal in meals:
            result=Meal.accumulateListOfDictionaries(list1=result,list2=meal.nutritionalInfoBasic)
        totalQuant = Meal.accumulateDailyQuantity(day,user)
        for nutrient in result:
            if nutrient['unit']=='g':
                nutrient['fraction'] = round(nutrient['quant']/totalQuant*100,2)
        return result

    @staticmethod
    def accumulateListOfDictionaries(list1,list2):
        """ list1 is the storage list list 2 is teh new list to be added"""
        result=list1
        for element2 in list2:
            found=False
            for element1 in result:
                if element1['name']==element2['name']:
                    element1['quant']=round(float(element1['quant']) + float(element2['quant']),2)
                    found=True
                    break
            if not found:
                element2['quant']=round(float(element2['quant']),2)
                result.append(element2)
        return result
    
    @staticmethod
    def getNutrientsPlot(day,user):
        import plotly.graph_objects as go
        from plotly.offline import plot
        from plotly.subplots import make_subplots
        import pandas as pd

        data = Meal.accumulateDailyNutrients(day,user)
        df = pd.DataFrame(data)
        if not df.empty:
            df1 = df[df['fraction'].notna()]
            df1 = df1.sort_values(by='fraction',ascending=False)
            fig = make_subplots(rows=1,specs=[[{"secondary_y": False}]])
            fig.update_yaxes(title_text=str(_("Distribucion de macronutrientes")), secondary_y=False)
            fig.add_trace(go.Bar(x=df1.name.values, y=df1.fraction.values,
                                 text=df1.fraction.values,textposition='auto',
                                 name=str(_("Distribucion de macronutrientes")),offsetgroup=1),secondary_y=False,)
            fig.update_traces(texttemplate='%{text:.2s}%')
            fig.update_layout(
                barmode='group',
                bargap=0.0, # gap between bars of adjacent location coordinates.
                bargroupgap=0, # gap between bars of the same location coordinate.
                margin=dict(l=20, r=20, t=20, b=20),
                )
            return plot({'data': fig}, output_type='div')
        else:
            return _("No hay datos para mostrar")



