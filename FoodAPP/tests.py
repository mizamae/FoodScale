from django.test import tag,TestCase,Client, TransactionTestCase
from time import sleep
from django.utils import timezone
from django.core.cache import cache
from celery.contrib.testing.worker import start_worker
from main.celery import app
from django.forms import ValidationError
import copy
from .models import Ingredient, CombinationPosition, Meal
from UsersAPP.models import User

print('######################################')
print('# TESTING OF FoodAPP MODEL FUNCTIONS #')
print('######################################')

def createIngredients():
    ingredients = [
                    { "id":i,"name":"Ingredient "+str(i),
                     "nutrients":
                            {
                                "grasas": [
                                    {
                                    "name": "Acido graso 22:6 n-3 (Acido docosahexaenoico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acidos grasos, monoinsaturados totales",
                                    "unit": "g",
                                    "quant": 9.3
                                    },
                                    {
                                    "name": "Acidos grasos, poliinsaturados totales",
                                    "unit": "g",
                                    "quant": 2.9
                                    },
                                    {
                                    "name": "Acidos grasos saturados totales",
                                    "unit": "g",
                                    "quant": 8.3
                                    },
                                    {
                                    "name": "Acido graso 12:0 (laurico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 14:0 (Acido miristico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 16:0 (Acido palmÃ\u00adtico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 18:0 (Acido estearico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 18:1 n-9 cis (Acido oleico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "colesterol",
                                    "unit": "mg",
                                    "quant": 80
                                    },
                                    {
                                    "name": "Acido graso 18:2",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 18:3",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 20:4 n-6  (Acido araquidonico)",
                                    "unit": "-",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Acido graso 20:5 (Acido eicosapentaenoico)",
                                    "unit": "-",
                                    "quant": 0
                                    }
                                ],
                                "minerales": [
                                    {
                                    "name": "calcio",
                                    "unit": "mg",
                                    "quant": 7
                                    },
                                    {
                                    "name": "hierro, total",
                                    "unit": "mg",
                                    "quant": 0.7
                                    },
                                    {
                                    "name": "potasio",
                                    "unit": "mg",
                                    "quant": 330
                                    },
                                    {
                                    "name": "magnesio",
                                    "unit": "mg",
                                    "quant": 21
                                    },
                                    {
                                    "name": "sodio",
                                    "unit": "mg",
                                    "quant": 1760
                                    },
                                    {
                                    "name": "fosforo",
                                    "unit": "mg",
                                    "quant": 190
                                    },
                                    {
                                    "name": "ioduro",
                                    "unit": "ug",
                                    "quant": 7
                                    },
                                    {
                                    "name": "selenio, total",
                                    "unit": "ug",
                                    "quant": 12
                                    },
                                    {
                                    "name": "zinc (cinc)",
                                    "unit": "mg",
                                    "quant": 2.2
                                    }
                                ],
                                "vitaminas": [
                                    {
                                    "name": "Vitamina A equivalentes de retinol de actividades de retinos y carotenoides",
                                    "unit": "ug",
                                    "quant": 0
                                    },
                                    {
                                    "name": "Vitamina D",
                                    "unit": "ug",
                                    "quant": 0.6
                                    },
                                    {
                                    "name": "Viamina E equivalentes de alfa tocoferol de actividades de vitameros E",
                                    "unit": "mg",
                                    "quant": 0.07
                                    },
                                    {
                                    "name": "folato, total",
                                    "unit": "ug",
                                    "quant": 2
                                    },
                                    {
                                    "name": "equivalentes de niacina, totales",
                                    "unit": "mg",
                                    "quant": 7
                                    },
                                    {
                                    "name": "riboflavina",
                                    "unit": "mg",
                                    "quant": 0.16
                                    },
                                    {
                                    "name": "tiamina",
                                    "unit": "mg",
                                    "quant": 0.9
                                    },
                                    {
                                    "name": "Vitamina B-12",
                                    "unit": "ug",
                                    "quant": 1
                                    },
                                    {
                                    "name": "Vitamina B-6, Total",
                                    "unit": "mg",
                                    "quant": 0.46
                                    },
                                    {
                                    "name": "Vitamina C ",
                                    "unit": "mg",
                                    "quant": 0.000001
                                    }
                                ],
                                "proximales": [
                                    {
                                    "name": "alcohol (etanol)",
                                    "unit": "g",
                                    "quant": 0
                                    },
                                    {
                                    "name": "energia, total",
                                    "unit": "kcal",
                                    "quant": 292
                                    },
                                    {
                                    "name": "grasa, total (lipidos totales)",
                                    "unit": "g",
                                    "quant": 22.1
                                    },
                                    {
                                    "name": "proteina, total",
                                    "unit": "g",
                                    "quant": 23.4
                                    },
                                    {
                                    "name": "agua (humedad)",
                                    "unit": "g",
                                    "quant": 50.5
                                    }
                                ],
                                "hidratos de carbono": [
                                    {
                                    "name": "fibra, dietetica total",
                                    "unit": "g",
                                    "quant": 0
                                    },
                                    {
                                    "name": "carbohidratos",
                                    "unit": "g",
                                    "quant": 0
                                    }
                                ]
                                }
                    }
                    for i in range (5)    
                ]
    for consumable in ingredients:
        Ingredient.objects.create(**consumable)

def createMeals():
    lunch = Meal.objects.create(**{'type':Meal.TYPE_LUNCH})
    lunch.appendIngredient(quantity=100,ingredient=Ingredient.objects.get(id=1))

@tag('Ingredients')
class Ingredients_tests(TransactionTestCase):
    ''' ASPECTS ALREADY TESTED:
        - 
    '''
    fixtures=[]
    

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.celery_worker = start_worker(app,perform_ping_check=False)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.celery_worker.__exit__(None, None, None)

    def setUp(self):
        cache.clear()
        createIngredients()
        createMeals()


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
             
# INDIVIDUAL FUNCTIONS TESTING
    def test_1(self):
        lunch = Meal.objects.get(type=Meal.TYPE_LUNCH)
        ingredient = Ingredient.objects.get(id=1)
        #print(str(ingredient.basicInfo))
        print('## Checks the basicInfo of ingredients and nutritionalInfoBasic of meals yield the same result if meal has only one ingredient ##')
        self.assertListEqual(ingredient.basicInfo,lunch.nutritionalInfoBasic)

        print('## Checks appending the same ingredient modifies the COmbinationPosition  ##')
        lunch.appendIngredient(quantity=100,ingredient=ingredient)
        ingredientContent = ingredient.scaledBasicInfo(weight=200)
        self.assertListEqual(ingredientContent,lunch.nutritionalInfoBasic)
        self.assertEqual(200,lunch.getQuantityIngredient(ingredient=ingredient))

        